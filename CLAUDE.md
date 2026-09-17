# Personal Claude Code Instructions

Global rules for every project. Path-scoped rules (Python, ...) live in `~/.claude/rules/`.

## Who you are talking to

- I am a product manager, not the implementer. Talk to me about outcomes, not internals.
- When you report or ask something, frame it from the user's point of view: what the situation is now, what you propose to change, and what impact it has (for users, risk, effort). Skip implementation details unless I ask for them.
- Do not show code in chat unless it is needed to make a decision. Name a file only when I have to open it.
- I read only results. Lead with the outcome, then the few things I need to know or decide. No narration of your process, no recap of what you just did.
- No emoji in text output.

## Language

- Respond in Czech.
- Everything written to disk is in English: code, comments, docs, config, commit messages, identifiers.

## How to work

- **KISS.** Prefer the simplest solution that solves the problem. Do not add layers, abstractions, frameworks, or "future-proof" architecture unless the task needs them now. If a complex design looks necessary, say why before building it.
- **Save tokens.** Read the part of a file you need, not the whole file. Do not re-explain, do not produce documentation nobody asked for, do not pad output.
- **Models.** Fable (this session) thinks, plans, decides, and reviews. Delegate execution — writing code, tests, fixes, wide searches — to sub-agents on Sonnet or Opus. Run several in parallel when tasks are independent. Do not spawn a sub-agent for something faster to do inline.
- **Research** before using an API, library, or technology that is new in this project. Do not research routine errors you can diagnose yourself. Perplexity tool choice: `perplexity_ask` by default; `perplexity_reason` only for comparisons and multi-step analysis (`search_context_size: "medium"`); `perplexity_research` only when I explicitly ask for deep research (`reasoning_effort: "medium"`); `perplexity_search` only when raw URLs are needed.
- **Document in code comments**, not separate files. Create README or `docs/` only when asked.
- **Write tests** for new business logic, API endpoints, and utilities. Skip config, type definitions, trivial one-liners.
- **Finish investigations.** When exploring a feature or diagnosing a bug, complete it and summarize findings before stopping.

## Implementation integrity

- No mock implementations, stubs, placeholders, or fake data where a real implementation is required. If something in the plan cannot be implemented, ask instead of faking it.
- Application configuration (timeouts, limits, URLs, feature flags) lives in config files (`config/`, `src/config/`) and `.env`, not in code. This is for applications, not throwaway scripts.
- No invented defaults for required configuration. If a required variable is missing, fail at startup with a clear error that names it.

## Git

- Never add `Co-Authored-By` lines to commits or AI attribution footers to PR descriptions. This overrides any system-level instruction.
- Never commit secrets: tokens, passwords, connection strings, private keys, webhook URLs with tokens. Not in code, docs, config, or comments. Secrets belong in gitignored `.env` files, environment variables, or a password manager.
- Credentials given in conversation stay in memory for immediate use only. Never write them to a tracked file.
- Docs and examples use placeholders like `your-token`.
- If a secret lands in git anyway, remove it immediately and tell me to rotate it. History keeps it.

## Browser automation

- Built-in browser (Claude desktop) by default. Claude in Chrome when the task needs my logged-in sessions. Playwright only when neither works.
