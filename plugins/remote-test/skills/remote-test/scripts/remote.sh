# Runs ON the test box (Linux, or WSL Ubuntu). Fed over SSH by run.sh, which
# prepends `export RT_PROJECT=... RT_BASE=... RT_WORKERS=... RT_CPUS=... GH_TOKEN=...`
# and a `set -- <ref> [pytest args...]` line. Not meant to be run locally.
set -euo pipefail
PROJECT="${RT_PROJECT:?missing project}"
CONF=/etc/remote-test.conf

# A shared box lists every user in $CONF (root-owned, one line per user and project):
#   <linux user> <project|*> <cpu list, e.g. 48-57> [base dir, default ~/remote-test/<project>]
# The admin hands out CPU ranges there, so users never fight over cores.
# Without the file (a personal box) nothing is pinned and run.sh passes the base dir.
CONF_CPUS=""; CONF_BASE=""
if [ -z "${RT_BASE:-}" ]; then
    [ -r "$CONF" ] || { echo "no $CONF on this box: ask its admin to add you (see SKILL.md, 'Adding a user')"; exit 2; }
    LINE="$(awk -v u="$(id -un)" -v p="$PROJECT" '!/^[[:space:]]*#/ && $1==u && ($2==p || $2=="*") {print; exit}' "$CONF")"
    [ -n "$LINE" ] || { echo "user $(id -un) has no line for '$PROJECT' in $CONF: ask the box admin to add one"; exit 2; }
    read -r _ _ CONF_CPUS CONF_BASE <<<"$LINE"
fi
BASE="${RT_BASE:-${CONF_BASE:-$HOME/remote-test/$PROJECT}}"
BASE="${BASE/#\~/$HOME}"
# An explicit REMOTE_TEST_CPUS may only narrow the user's range, never leave it.
RT_CPUS="${RT_CPUS:-$CONF_CPUS}"
if [ -n "$CONF_CPUS" ] && [ "$RT_CPUS" != "$CONF_CPUS" ]; then
    expand() { local r out=(); for r in ${1//,/ }; do out+=($(seq "${r%-*}" "${r#*-}")); done; echo "${out[@]}"; }
    ALLOWED=" $(expand "$CONF_CPUS") "
    for c in $(expand "$RT_CPUS"); do
        [[ "$ALLOWED" == *" $c "* ]] || { echo "CPU $c is outside your range $CONF_CPUS in $CONF"; exit 2; }
    done
fi
if [ -n "${RT_WORKERS:-}" ]; then
    WORKERS="$RT_WORKERS"
elif [ -n "$RT_CPUS" ]; then
    WORKERS=0
    for r in ${RT_CPUS//,/ }; do WORKERS=$(( WORKERS + ${r#*-} - ${r%-*} + 1 )); done
else
    WORKERS=logical
fi
mkdir -p "$BASE/bin"
export PATH="$BASE/bin:$HOME/.local/bin:$PATH"

# Per-project settings. NAME keeps the on-box dir names the Agnes setup has
# always used (<base>/agnes, <base>/agnes-runs, <base>/agnes-tmp).
case "$PROJECT" in
    agnes)
        NAME=agnes
        REPO_URL="https://github.com/keboola/agnes-the-ai-analyst.git"
        PY=3.13
        DEFAULT_ARGS=(tests/ connectors/)
        NEEDS_NODE=1 ;;
    kbagent)
        NAME=kbagent
        REPO_URL="https://github.com/keboola/cli.git"
        PY=3.12  # CI's PR interpreter
        DEFAULT_ARGS=(tests/)
        NEEDS_NODE=0 ;;
    *) echo "unknown project $PROJECT"; exit 2 ;;
esac

# A full run wants ~10+ GB of pytest basetemp (WSL's /tmp is small). No leading
# dot in the name: some tests derive a file "extension" from the whole path.
export TMPDIR="$BASE/$NAME-tmp"
mkdir -p "$TMPDIR"

# GitHub auth from the token run.sh streamed in; nothing is stored on disk.
if [ -n "${GH_TOKEN:-}" ]; then
    printf '#!/bin/sh\ncase "$1" in *sername*) echo x-access-token ;; *) echo "$GH_TOKEN" ;; esac\n' > "$BASE/bin/git-askpass-env"
    chmod 700 "$BASE/bin/git-askpass-env"
    export GIT_ASKPASS="$BASE/bin/git-askpass-env" GIT_TERMINAL_PROMPT=0
fi

command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$BASE/bin" sh >/dev/null 2>&1; }

# Agnes UI tests shell out to `node` (GitHub's ubuntu runners ship it; CI pins 22).
if [ "$NEEDS_NODE" = 1 ] && ! command -v node >/dev/null; then
    echo "== installing Node.js 22 into $BASE/node"
    V="$(curl -fsSL https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt | grep -o 'node-v[0-9.]*-linux-x64.tar.xz' | head -1)"
    mkdir -p "$BASE/node"
    curl -fsSL "https://nodejs.org/dist/latest-v22.x/$V" | tar -xJ --strip-components=1 -C "$BASE/node"
    ln -sf "$BASE/node/bin/node" "$BASE/bin/node"
fi

REF="${1:?missing branch or PR number}"; shift
REPO="$BASE/$NAME"
RUNS="$BASE/$NAME-runs"
mkdir -p "$RUNS"

# One run per project at a time: two full suites in parallel would fight over
# CPU, RAM and the shared pytest basetemp.
exec 9>"$RUNS/.lock"
if ! flock -n 9; then
    echo "BUSY: another $PROJECT test run is in progress on this machine"
    exit 75
fi

if [ ! -d "$REPO/.git" ]; then
    # Shallow: the box pulls straight from GitHub, history is not needed.
    git clone -q --depth 50 "$REPO_URL" "$REPO"
fi
cd "$REPO"

if [[ "$REF" =~ ^#?[0-9]+$ ]]; then
    SRC="pull/${REF#\#}/head"
else
    SRC="refs/heads/$REF"
fi
# origin/main too: Agnes's `--lane impacted` diffs against it.
git fetch -q --depth 50 origin "+refs/heads/main:refs/remotes/origin/main"
git fetch -q --depth 50 origin "$SRC"
git checkout -q --force --detach FETCH_HEAD
# Deepen both shallow histories until they meet, so a diff against the
# merge-base with origin/main sees the real change.
for _ in 1 2 3 4 5 6 7 8 9 10; do
    git merge-base origin/main HEAD >/dev/null 2>&1 && break
    git fetch -q --deepen 200 origin "+refs/heads/main:refs/remotes/origin/main" "$SRC"
done
git clean -qfdx -e .venv

# The checkout may be someone else's PR: its install scripts and tests must not
# see the user's GitHub token, so drop it before running any of its code.
unset GH_TOKEN GIT_ASKPASS
rm -f "$BASE/bin/git-askpass-env"

# Reinstall deps only when the lock or project metadata changed (CI's install).
HASH="$(cat uv.lock pyproject.toml | sha256sum | cut -d' ' -f1)"
if [ ! -x .venv/bin/python ] || [ "$(cat .venv/.lockhash 2>/dev/null)" != "$HASH" ]; then
    echo "== installing dependencies from uv.lock"
    rm -rf .venv
    if [ "$PROJECT" = agnes ]; then
        uv venv -q --python "$PY" .venv
        UV_LINK_MODE=copy INSTALL_PYTHON=.venv/bin/python sh scripts/ci/install-from-lock.sh dev server extraction >"$RUNS/install.log" 2>&1 \
            || { echo "install failed, see $RUNS/install.log"; tail -n 20 "$RUNS/install.log"; exit 1; }
    else
        UV_LINK_MODE=copy UV_PYTHON="$PY" uv sync -q --extra server >"$RUNS/install.log" 2>&1 \
            || { echo "install failed, see $RUNS/install.log"; tail -n 20 "$RUNS/install.log"; exit 1; }
    fi
    echo "$HASH" > .venv/.lockhash
fi

# No path among the args: run what CI runs.
HAS_PATH=0
for a in "$@"; do
    [[ "$a" != -* && -e "${a%%::*}" ]] && HAS_PATH=1
done
[ "$HAS_PATH" = 1 ] || set -- "${DEFAULT_ARGS[@]}" "$@"

EXTRA=()
if [ "$PROJECT" = agnes ]; then
    # The repo refuses broad local runs unless told this is deliberate; this box
    # exists for exactly that. Older branches lack the flag, so pass it only when known.
    grep -q -- "--broad-local" conftest.py tests/conftest.py 2>/dev/null && EXTRA=(--broad-local)
else
    # CI deselects tests that need real API credentials, unless a -m was given.
    HAS_M=0
    for a in "$@"; do [ "$a" = -m ] && HAS_M=1; done
    [ "$HAS_M" = 1 ] || EXTRA=(-m "not integration")
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="$RUNS/$STAMP-${REF//[^A-Za-z0-9._-]/_}.log"
echo "== project: $PROJECT"
echo "== ref:    $REF"
echo "== commit: $(git log -1 --format='%h %s')"
echo "== box:    $(nproc) CPUs, $(free -g | awk '/^Mem/{print $2}') GB RAM"
echo "== args:   $* ${EXTRA[*]}"
echo "== log:    $LOG"

# Shared box: pin to the project's CPU range and run below the box's services.
PIN=()
if [ -n "${RT_CPUS:-}" ]; then
    PIN=(taskset -c "$RT_CPUS")
fi
echo "== workers: $WORKERS${RT_CPUS:+ on CPUs $RT_CPUS}"

START=$(date +%s)
set +e
TESTING=1 "${PIN[@]}" nice -n 10 .venv/bin/python -m pytest "$@" -n "$WORKERS" --dist "${RT_DIST:-worksteal}" -q --tb=short -rfE -p no:cacheprovider "${EXTRA[@]}" >"$LOG" 2>&1
RC=$?
set -e

# Stream back only the summary: the link to the box is slow, the full log
# stays on the box.
echo "== pytest exit code: $RC after $(( $(date +%s) - START ))s"
if [ "$RC" = 0 ]; then
    tail -n 1 "$LOG"
elif grep -q "short test summary info" "$LOG"; then
    awk '/short test summary info/{f=1} f && n++ < 150' "$LOG"
    tail -n 1 "$LOG"
else
    tail -n 40 "$LOG"
fi
exit $RC
