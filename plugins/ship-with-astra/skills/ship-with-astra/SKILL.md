---
name: ship-with-astra
description: End-to-end delivery of a change with GPT Astra as the second pair of eyes - design, Astra design consultation, build, PR, Astra PR review, then auto-fix and auto-merge. Use when Petr says /ship-with-astra, "navrhni, zkonzultuj s Astrou, udělej a mergni", or asks for the design -> Astra -> build -> PR -> review -> auto-merge loop.
---

# Ship with Astra

One loop, in this order. The user is a product manager: report outcomes in Czech,
no code in chat, PR states exactly as `gh` reports them.

## 1. Design (short)

- Ground it in evidence first: reproduce the problem, read the code paths involved.
- Write a self-contained brief to the session scratchpad (`brief1.md`): context,
  what exists, the incident or goal with measured facts, the proposed design as
  numbered decisions, what is deliberately out of scope, and lettered questions.
- Branch from fresh `origin/main` before Astra reads the repo, so it reviews current code.

## 2. Consult GPT Astra on the design

Use the `second-opinion` skill. Run from the repo root, in the background:

```bash
codex exec -m gpt-6-astra -c model_reasoning_effort="high" -s read-only \
  --skip-git-repo-check -o "$S/r1.md" "$(cat "$S/brief1.md")" < /dev/null
```

- Incorporate or explicitly rebut every finding. A second round
  (`codex exec resume --last ...`) only when a disagreement matters; stop after 2-3.
- Write the final design to `$S/design.md`: the numbered decisions plus a numbered
  "Risks to handle" list with EVERY risk and edge case Astra raised, each with how
  it is handled (which decision, which test) or why it is rejected. Nothing Astra
  raised is dropped silently: a risk that reaches the builder only half is how bugs ship.
- Give the user a short summary: the final design, what Astra changed, what you
  rejected and why. Proceed without waiting unless a decision is genuinely theirs
  (scope change, new cloud dependency, product behaviour change).

## 3. Build

- Slice the work so each PR has one concern and can be reviewed in one pass
  (rule of thumb: one data area, one surface family). A PR with many tables,
  concurrency and several surfaces at once is too big: split it before building.
- Delegate each slice to a builder sub-agent (`agnes-builder` in the Agnes repo,
  otherwise `general-purpose`) with the full `design.md`, risk list included. Tell it explicitly:
  - TDD: write the failing test first; a bug fix starts with a test that fails without it.
  - Each of these failure scenarios that applies to the change gets its own test
    (name the applicable ones in the brief, skip the rest):
    partial success then retry; a retry after a commit whose response was lost;
    a swallowed error in a helper that "never raises"; concurrent requests;
    a switch or config toggled mid-operation; access revoked mid-operation.
  - The invariants checklist, self-checked before handing back:
    one global lock order for every operation that locks the same rows;
    a state change and its side-table writes in one transaction;
    caller identity only from the authenticated principal, never from an argument
    the caller controls; explicit empty differs from omitted; every new path
    behaves with its switch off and on every supported backend; values that cannot
    be stored (NaN, binary) are rejected before hashing or saving.
  - Push the branch but do NOT open the PR. The PR is opened only after steps 4-6 are clean.
  - Do NOT run tests locally (CPU); lint/type checks only, touched tests remotely if available.
  - No `Co-Authored-By` trailer, no AI attribution anywhere.
  - Repo rules (Agnes: no code comments, changelog fragment, PG-only Alembic migration,
    runtime config, user docs page updated when user-visible).
- Read the diff yourself as a hostile reviewer (races, retries after partial success,
  limits, timeouts, auth edge cases, secrets in messages) and fix what you find.

## 4. Review against the design

A diff read and a generic review miss what the design promised but the code does
not do. Spawn a fresh reviewer that did not write the design
(`agnes-reviewer-adversarial` in the Agnes repo, otherwise `general-purpose`).
Give it `design.md`, Astra's design-review findings (`r1.md`, later rounds too)
and the branch. It returns a checklist:

- Every decision and every risk marked implemented / not / partial, with file:line evidence.
- Every claimed defect proven: a script that fails, or a concrete input -> wrong output.
  Unproven claims are not findings.

## 5. Astra review of the branch (before the PR)

Run it in parallel with step 4. Pass the risk list, not a bare `codex exec review`
(which cannot take a prompt together with `--base`). Write `$S/pr-review.md`:
"Review `git diff origin/main...HEAD` for bugs. For each risk below, say whether the
diff handles it, with file:line; then list other defects, each with a concrete failing
input. Check especially: lock order across all operations on the same rows,
transaction boundaries, identity taken from arguments, switch-off and other-backend paths."
followed by the "Risks to handle" list from `design.md`.

```bash
codex exec -m gpt-6-astra -c model_reasoning_effort="high" -s read-only \
  --skip-git-repo-check --ephemeral -o "$S/review.md" "$(cat "$S/pr-review.md")" < /dev/null
```

## 6. Fix loop (until clean, still before the PR)

- Merge the findings of steps 4 and 5 into one list; the builder fixes all of them,
  each with a regression test, and commits WITHOUT pushing.
- Astra reviews the fix diff (`git diff <last reviewed SHA>..HEAD`) before the push:
  fixes are where new concurrency and atomicity bugs come from. Fix what it finds.
- One push per round. Repeat until a round has no valid findings; rebut invalid ones
  in the report.

## 7. Pull request

- Open a ready (non-draft) PR only now. Body: what changed for users, why, how it was
  verified (both reviews clean, remote tests), what is deliberately not included. No AI footer.
- Devin and CI findings after the PR follow the same loop: batch them, fix all,
  Astra on the fix diff, one push. Never push fixes piecemeal: every push restarts
  Devin and CI.

## 8. Arm the PR

- Desktop app: `ccd_pr` `get_status` (bind the PR if needed), then `set_monitor`
  with auto-fix + address comments, and `set_auto_merge`.
- Elsewhere: `gh pr merge <N> --merge --auto`.
- Done means MERGED: if the session continues, follow CI and review comments until
  the PR is MERGED; otherwise list exactly what is pending.
- After EVERY push to the PR (fix, review answer, conflict merge) read the live state
  (`ccd_pr get_status` or `gh pr view --json autoMergeRequest`). A merge-queue
  ejection (e.g. `merge_conflict`) or a push silently drops auto-merge; re-arm it
  immediately. Never report AUTO-MERGE ENABLED from memory, only from that read.
  A PR left un-armed after a conflict fix sits outside the queue while other
  migrations land, and every one of them costs another conflict and CI run.

## Report

Czech, outcome first: the problem, the final design in a few bullets, what Astra
changed, the PR link and its literal state (OPEN / CI RUNNING / AUTO-MERGE ENABLED / MERGED).
