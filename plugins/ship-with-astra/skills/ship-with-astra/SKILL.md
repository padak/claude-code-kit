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
- Give the user a short summary: the final design, what Astra changed, what you
  rejected and why. Proceed without waiting unless a decision is genuinely theirs
  (scope change, new cloud dependency, product behaviour change).

## 3. Build

- Delegate to a builder sub-agent (`agnes-builder` in the Agnes repo, otherwise
  `general-purpose`) with the final design. Tell it explicitly:
  - TDD: write the failing test first; a bug fix starts with a test that fails without it.
  - Do NOT run tests locally (CPU); lint/type checks only. CI runs the tests.
  - No `Co-Authored-By` trailer, no AI attribution anywhere.
  - Repo rules (Agnes: no code comments, changelog fragment, PG-only Alembic migration,
    runtime config, user docs page updated when user-visible).
- Read the diff yourself as a hostile reviewer (races, retries after partial success,
  limits, timeouts, auth edge cases, secrets in messages) and fix what you find.

## 4. Pull request

- Push and open a ready (non-draft) PR. Body: what changed for users, why, how it
  was verified, what is deliberately not included. No AI footer.

## 5. Astra review of the PR

```bash
codex exec review --base main -m gpt-6-astra -c model_reasoning_effort="high" \
  --ephemeral -o "$S/review.md" < /dev/null
```

- Fix every valid finding with a regression test; rebut the rest in a PR comment
  only if the user asked for comments, otherwise note it in the report.

## 6. Arm the PR

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
