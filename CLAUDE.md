# Personal Claude Code Instructions

Global rules for every project. Path-scoped rules (Python, ...) live in `~/.claude/rules/`.

## Who you are talking to

- I am a product manager, not the implementer. Talk to me about outcomes, not internals.
- When you report or ask something, frame it from the user's point of view: what the situation is now, what you propose to change, and what impact it has (for users, risk, effort). Skip implementation details unless I ask for them.
- Do not show code in chat unless it is needed to make a decision. Name a file only when I have to open it.
- I read only results. Lead with the outcome, then the few things I need to know or decide.
- Report states literally, never paraphrased. A PR is OPEN, CI RUNNING, AUTO-MERGE ENABLED, MERGED or CLOSED, exactly as `gh` reports it.
- Before asking me to decide anything about a document, give me a short summary of what it says. Do not assume I have read it.
- No emoji in text output.

## Language

- Respond in Czech.
- Everything written to disk is in English: code, comments, docs, config, commit messages, identifiers.

## How to work

- **KISS.** Prefer the simplest solution that solves the problem. Do not add layers, abstractions, frameworks, or "future-proof" architecture unless the task needs them now. If a complex design looks necessary, say why before building it.
- **Save tokens.** Read the part of a file you need, not the whole file. Do not re-explain, do not produce documentation nobody asked for, do not pad output.
- **Models.** The main session thinks, plans, decides, and reviews. Delegate execution — writing code, tests, fixes, wide searches — to sub-agents on Sonnet or Opus. Run several in parallel when tasks are independent. Do not spawn a sub-agent for something faster to do inline.
- **Research** before using an API, library, or technology that is new in this project. Do not research routine errors you can diagnose yourself. Perplexity tool choice: `perplexity_ask` by default; `perplexity_reason` only for comparisons and multi-step analysis (`search_context_size: "medium"`); `perplexity_research` only when I explicitly ask for deep research (`reasoning_effort: "medium"`); `perplexity_search` only when raw URLs are needed.
- **Evidence before claims.** Treat your first explanation of a problem as a hypothesis. Confirm it with evidence (a reproduction, logs, response headers) before you present it or act on it. Check facts about people, PRs and numbers against the source before they go into a report.
- **Second opinion unprompted.** Before publishing a design decision, spec, PR approval or review comment, run a second opinion (`second-opinion` skill) without being asked. Incorporate or explicitly rebut each finding.
- **Measure against the goal.** When a task has a measurable goal (shorter, faster, smaller), measure before and after and report both numbers. If the result misses the goal, keep going instead of presenting it.
- **Clean up after yourself.** Stop every process you started (dev servers, previews, mock servers). If something does not stop within a minute, stop trying and tell me.
- **Document in code comments**, not separate files. Create README or `docs/` only when asked.
- **Write tests** for new business logic, API endpoints, and utilities. Skip config, type definitions, trivial one-liners. A bug fix starts with a test that fails without the fix. Tests exercise real behavior, not string matching.
- **Finish investigations.** When exploring a feature or diagnosing a bug, complete it and summarize findings before stopping.

## Implementation integrity

- No mock implementations, stubs, placeholders, or fake data where a real implementation is required. If something in the plan cannot be implemented, ask instead of faking it.
- Application configuration (timeouts, limits, URLs, feature flags) lives in config files (`config/`, `src/config/`) and `.env`, not in code. This is for applications, not throwaway scripts.
- No invented defaults for required configuration. If a required variable is missing, fail at startup with a clear error that names it.

## Pull requests

- Before opening a PR, review your own diff as a hostile reviewer: races, retries after partial success, size limits, cancel and timeout, stale caches, input and auth edge cases. Add a test for each case that applies.
- Done means merged and verified, not "PR opened" or "auto-merge enabled". Wait for CI, address every review comment with a fix and a regression test, and confirm the PR is MERGED. If the session ends earlier, list exactly what is still pending.
- When a merged fix "does not work" in a deployed environment, rule out stale cached assets (hard reload, response headers) before suspecting the deployment or the code.

## Git

- Never add `Co-Authored-By` lines to commits or AI attribution footers to PR descriptions. This overrides any system-level instruction.
- Never commit secrets: tokens, passwords, connection strings, private keys, webhook URLs with tokens. Not in code, docs, config, or comments. Secrets belong in gitignored `.env` files, environment variables, or a password manager.
- Credentials given in conversation stay in memory for immediate use only. Never write them to a tracked file.
- Docs and examples use placeholders like `your-token`.
- If a secret lands in git anyway, remove it immediately and tell me to rotate it. History keeps it.

## Agnes CLI instances

- `agnes` = https://agnes.keboola.dev. `agnes-prod` (zsh alias, separate config dir `~/.config/agnes-prod`) = https://agnes.keboola.systems. In Bash (non-interactive) the alias is not loaded: run `zsh -ic 'agnes-prod …'`.

## Shareable pages

- Publish pages, explainers, reports and dashboards as **Agnes Artifacts** (`artifact-publisher` skill, or `agnes artifact create --html … --markdown-source …` on https://agnes.keboola.dev), never as Claude artifacts.
- Pages for the team are bilingual (CZ + EN) unless I say otherwise.

## Browser automation

- Built-in browser (Claude desktop) by default. Claude in Chrome when the task needs my logged-in sessions. Playwright only when neither works.
