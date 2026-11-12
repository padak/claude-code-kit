#!/usr/bin/env bash
# Run a project's pytest suite for a GitHub branch or PR on a remote Linux test box.
# Usage (from inside the project's checkout, or with REMOTE_TEST_PROJECT set):
#   bash run.sh <branch|PR-number> [pytest paths/options...]
# Exit code is pytest's (75 = box busy with another run of the same project,
# 255 = SSH failed, 2 = usage / unknown project / user missing from the box config).
#
# Projects (REMOTE_TEST_PROJECT, else detected from this checkout's origin URL):
#   agnes    - keboola/agnes-the-ai-analyst
#   kbagent  - keboola/cli
#   crm      - keboola/crm (API suite in api/, MySQL in Docker when the box user has it)
# Hosts (REMOTE_TEST_HOST, default rtx):
#   rtx (or any shared box) - CPU range and base dir per user come from
#            /etc/remote-test.conf on the box, so several people share it safely.
#   win-ts - Petr's home Windows laptop, WSL Ubuntu (16 CPUs), all workers.
set -euo pipefail

[ $# -ge 1 ] || { echo "usage: run.sh <branch|PR-number> [pytest args...]" >&2; exit 2; }
HERE="$(cd "$(dirname "$0")" && pwd)"
# AGNES_TEST_* are the names from before the skill became generic.
HOST="${REMOTE_TEST_HOST:-${AGNES_TEST_HOST:-rtx}}"

PROJECT="${REMOTE_TEST_PROJECT:-}"
if [ -z "$PROJECT" ]; then
    case "$(git remote get-url origin 2>/dev/null || true)" in
        *keboola/agnes-the-ai-analyst*) PROJECT=agnes ;;
        *keboola/cli*|*keboola_agent_cli*|*keboola-agent-cli*) PROJECT=kbagent ;;
        *keboola/crm|*keboola/crm.git) PROJECT=crm ;;
        *) echo "cannot tell the project from this directory; set REMOTE_TEST_PROJECT=agnes|kbagent|crm" >&2; exit 2 ;;
    esac
fi
case "$PROJECT" in
    agnes|kbagent|crm) ;;
    *) echo "unknown project '$PROJECT' (agnes|kbagent|crm)" >&2; exit 2 ;;
esac

WORKERS="${REMOTE_TEST_WORKERS:-${AGNES_TEST_WORKERS:-}}"
case "$HOST" in
    win-ts)
        REMOTE='wsl -- bash -s'
        # Agnes predates the per-project dirs and lives straight in ~ there.
        case "$PROJECT" in
            agnes) BASE='$HOME' ;;
            kbagent) BASE='$HOME/kbagent-petr' ;;
            *) BASE="\$HOME/remote-test/$PROJECT" ;;
        esac
        # Explicit count: Agnes' conftest caps `-n logical/auto` to 6 locally; 12 fits the 27 GB WSL RAM.
        WORKERS="${WORKERS:-12}"; CPUS="" ;;
    *)
        # Base dir and CPU range are read on the box from /etc/remote-test.conf.
        REMOTE='bash -s'; BASE=""; CPUS="${REMOTE_TEST_CPUS:-}" ;;
esac

# The GitHub token travels inside the SSH stream and lives only in the remote
# shell's environment, so it is never written to the box's disk.
TOKEN="$(gh auth token 2>/dev/null || true)"

# Args travel on stdin as a `set --` line, so the remote login shell (cmd.exe /
# wsl.exe on win-ts) never sees or mangles them. The SSH session stays open for
# the whole run: on win-ts, WSL kills the tests once no wsl.exe client is attached.
{
    printf 'export RT_PROJECT=%q RT_BASE="%s" RT_WORKERS=%q RT_CPUS=%q GH_TOKEN=%q\n' \
        "$PROJECT" "$BASE" "$WORKERS" "$CPUS" "$TOKEN"
    printf 'set --'; printf ' %q' "$@"; printf '\n'
    cat "$HERE/remote.sh"
} | ssh -o ServerAliveInterval=15 -o ConnectTimeout=15 "$HOST" "$REMOTE"
