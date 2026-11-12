---
name: remote-test
description: Use when a pytest suite, or a large part of it, needs to run for a branch or PR of Agnes (keboola/agnes-the-ai-analyst) or kbagent (keboola/cli), or when the user asks to test "na serveru", "na rtx", "doma", "na windows", "na test stroji" or "remote" - running test suites locally overloads the laptop.
---

# Remote test box

A remote Linux box runs the project's pytest suite so the laptop does not have to.
The box clones from GitHub itself; nothing is copied from the laptop.

## Projects

The project is detected from the current checkout's `origin` URL;
`REMOTE_TEST_PROJECT=agnes|kbagent` overrides it.

| Project | Repo | Python | Default args (no path given) |
|---|---|---|---|
| `agnes` | keboola/agnes-the-ai-analyst | 3.13 | `tests/ connectors/` + `--broad-local`, `TESTING=1` |
| `kbagent` | keboola/cli | 3.12 (CI's PR interpreter) | `tests/` + `-m "not integration"` unless you pass `-m` |

## Hosts

| Host (`REMOTE_TEST_HOST`) | Box | Where CPUs and dirs come from |
|---|---|---|
| `rtx` (default) | shared Keboola server, 64 CPUs, 223 GB, also serves LLM inference, `nice 10` | `/etc/remote-test.conf` on the box, one line per Linux user and project |
| `win-ts` | Petr's home Windows laptop (8 cores / 16 threads), WSL Ubuntu, 27 GB; full Agnes suite ~48 min vs ~11 min on rtx | fixed in `run.sh`: Agnes in `~`, kbagent in `~/kbagent-petr`, 12 workers, no pinning |

`rtx` is the SSH alias in your `~/.ssh/config`; any other alias works the same
way as long as the box has `/etc/remote-test.conf`.

On a shared box each user runs under their own Linux account and gets a CPU
range from the box config. The worker count equals the number of CPUs in that
range. `REMOTE_TEST_WORKERS` overrides the worker count; `REMOTE_TEST_CPUS` can
only narrow the range (asking for a CPU outside it fails with exit 2). If you
have one range for both projects (`*`), a run of each at the same time shares it.

**Only code pushed to GitHub can be tested.** The script fetches the branch or
PR from `origin`; local commits and uncommitted edits are invisible to it.
Push first (to a branch, never to main).

## Run

From inside the project's checkout:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/remote-test/scripts/run.sh" <branch|PR-number> [pytest paths/options]
```

| Goal | Args after the ref |
|---|---|
| Full suite, like CI | none |
| Specific tests | paths, e.g. `tests/test_foo.py -x` |
| Agnes: only tests the diff vs main touches | `--lane impacted` |
| Agnes: fast smoke set | `--lane smoke` |

- A number (quote `"#4710"` if you use `#`) is a PR: tests `pull/N/head`, the PR
  head, not CI's merge commit.
- Always `--dist worksteal` (`RT_DIST` on the box overrides).
- Exit code is pytest's: 0 green, 1 failures, 5 nothing collected (wrong path or
  `-k`). `75` = another run of the same project by the same user holds the box.
  `2` = usage error, or your user has no line in `/etc/remote-test.conf`.
  `255` = SSH failed.
- GitHub auth: run.sh streams `gh auth token` over SSH for each run; it is
  never stored on the box.
- Environment variables for the tests themselves (e.g. kbagent's
  `SYNC_WALK_SEEDS`) are not forwarded. For a one-off, prefix the command on
  the box by hand after one normal run has prepared the checkout:
  `ssh rtx 'cd <base>/kbagent && SYNC_WALK_SEEDS=500 taskset -c <your cpus> nice -n 10 .venv/bin/python -m pytest tests/test_sync_random_walk.py -n <workers> -q'`

Launch it with Bash `run_in_background: true` and wait for the completion
notice; do not poll. Keep the SSH session open for the whole run (on `win-ts`
WSL kills the tests when the last client disconnects); never `nohup`/detach.

## Output

Only the pytest summary comes back (`== pytest exit code`, FAILED/ERROR lines,
counts; the last 40 log lines if pytest died before its summary). The `== commit:`
line names the tested commit; check it matches what you meant to test. The
`== workers:` line shows the CPUs used. The full log stays on the box at the
`== log:` path:

```bash
ssh rtx 'bash -s' <<'X'
grep -n -A40 "test_name" <log path>
X
```

On `win-ts` use `ssh win-ts 'wsl -- bash -s'` with the same heredoc (its link is
~1 MB/s, fetch only what you need). Before explaining a failure, rerun just that
test (`run.sh <ref> tests/x.py::test_y`) to tell a real failure from a flaky one.

## Common problems

| Symptom | Fix |
|---|---|
| `cannot tell the project` | Run from inside the checkout or set `REMOTE_TEST_PROJECT`. |
| `no /etc/remote-test.conf` or `has no line for` | The box admin has not added your user yet (see below). |
| `fatal: couldn't find remote ref` | Branch not pushed or name misspelled. |
| `ssh: connect ... timed out` / `Permission denied (publickey)` | Box offline, or your key is not on it yet. Do not fall back to a local full run. |
| `BUSY` (exit 75) | Your own run of that project is in progress. Wait for it, do not kill it. |
| GitHub auth error on fetch | `gh auth status` on the laptop; the token comes from there. |
| `disk guard: Low disk` | Run `rm -rf <base>/<name>-tmp/pytest-of-*` on the box. |
| Workers killed / MemoryError | Only on `win-ts` (WSL RAM cap): run a subset. |

## Box layout

Per project `<name>` (`agnes` or `kbagent`) under the base dir from the box
config (default `~/remote-test/<name>`):
`<base>/<name>` repo (shallow, detached at the tested commit, reset each run) ·
`<base>/<name>/.venv`, reinstalled only when `uv.lock`/`pyproject.toml`
change · `<base>/<name>-runs/*.log` logs · `<base>/bin` uv, node (Agnes only),
git askpass helper · `<base>/<name>-tmp` pytest basetemp. The first run
installs uv, Python, the dependencies and (Agnes) Node, a few minutes.

## Adding a user (box admin)

The new user sends a public SSH key. On the box, as an admin with sudo:

```bash
sudo useradd -m -s /bin/bash <user>
sudo install -d -m 700 -o <user> -g <user> /home/<user>/.ssh
echo '<their public key>' | sudo tee /home/<user>/.ssh/authorized_keys >/dev/null
sudo chown <user>:<user> /home/<user>/.ssh/authorized_keys && sudo chmod 600 /home/<user>/.ssh/authorized_keys
echo '<user>  *  <free cpu range, e.g. 48-57>' | sudo tee -a /etc/remote-test.conf
```

Pick a range no other line uses (`cat /etc/remote-test.conf`). The user is
not added to `sudo` or any other group.

The new user then needs, on their laptop: this plugin, `gh` signed in with
read access to the repos they test, and an SSH alias:

```
Host rtx
    HostName <box hostname>
    User <user>
    IdentityFile ~/.ssh/<their key>
```

Check with `ssh rtx 'id -un; grep "^$(id -un) " /etc/remote-test.conf'`.

## win-ts setup

`win-ts` worker setup (2026-11-02): Tailscale runs only on Windows (direct from
outside via the home public IP); `tailscaled` in WSL is disabled, as Tailscale
recommends, because WSL's own NAT forced every outside connection through a DERP
relay. `ssh win-ts` lands in Windows cmd; `ssh win-wsl` lands in Linux via
`ProxyJump win-ts` to Windows `127.0.0.1:2222`, which wslrelay forwards to WSL
sshd (`Port 2222` in `/etc/ssh/sshd_config.d/10-wsl-port.conf`; Windows sshd
owns 22, so never point win-wsl at 22). Root in WSL without a password:
`ssh win-ts 'wsl -u root -- bash -s'`. Windows scheduled task "WSL keepalive" (at logon,
the laptop auto-logs in) runs a hidden `wsl.exe -d Ubuntu --exec sleep
infinity`, so the distro stays up with no client. `%USERPROFILE%\.wslconfig`:
`memory=28GB` (WSL sees 27 GB). Sleep and hibernate on idle are off; the laptop
only goes to sleep on a critical battery, so keep it on the charger. uv and node
live in `~/.local/bin` there and the GitHub token is also stored in `~/.git-credentials`.
Long Claude sessions: `tmux new -As claude`, then `claude --remote-control`.
Remove keepalive: `schtasks /delete /tn "WSL keepalive" /f`.
