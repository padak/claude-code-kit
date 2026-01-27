# Personal Claude Code Instructions

## Language

- **Communicate with user in Czech** (mluvíme česky)
- **Write all files in English** (code, comments, documentation, config files)
- Variable names, function names, commit messages - all in English

## Research

- **Use Perplexity MCP** when something is unclear or unfamiliar
- Before implementing unknown technology/API - research first
- When encountering errors or unexpected behavior - research
- When deciding between approaches - research to find best practices

## General

- Do NOT use emoji in text output
- When working on multiple independent tasks (e.g., writing multiple tests, fixing multiple files, implementing multiple features), use parallel sub-agents (Task tool) - spawn one agent per task for maximum speed
- Always have a plan (use TodoWrite) and mark tasks as completed when done
- Keep repo clean - don't generate unnecessary documentation files
- Write tests for anything that makes sense to test

## Configuration - Zero Hardcoded Values

- **NEVER hardcode** constants, values, or numbers directly in code
- All configuration must be in dedicated config files:
  - `config/` or `src/config/` folder for application settings
  - `.env` / `.env.local` for secrets and environment-specific values
- This applies to: timeouts, limits, URLs, feature flags, UI constants, etc.

```python
# BAD
MAX_RETRIES = 3
API_TIMEOUT = 30

# GOOD
from config import settings
max_retries = settings.api.max_retries
timeout = settings.api.timeout
```

## Configuration - No Silent Defaults

- **NEVER invent default values** for required configuration
- If a required variable is missing, **fail fast at startup** with a clear error message
- Do NOT silently fall back to made-up defaults that might cause unexpected behavior

```python
# BAD - silent fallback to invented value
database_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
api_key = os.getenv("API_KEY", "sk-placeholder-key")

# GOOD - fail fast with clear error
database_url = os.environ["DATABASE_URL"]  # Raises KeyError if missing

# GOOD - explicit validation at startup
def load_config():
    required = ["DATABASE_URL", "API_KEY", "ENCRYPTION_KEY"]
    missing = [var for var in required if var not in os.environ]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
```

```typescript
// TypeScript - GOOD
function getRequiredEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}
```

## Git Commits & Pull Requests

When creating git commits:
- Do NOT include "Co-Authored-By: Claude <noreply@anthropic.com>" in commit messages
- Keep commit messages clean and concise

When creating pull requests:
- Do NOT include "Generated with Claude Code" footer in PR description
- Keep PR descriptions clean and focused on the changes

## Python Projects

- Use `.venv` for virtual environment (create with `python -m venv .venv`)
- Keep all dependencies in single `requirements.txt` in project root
- After installing packages, update requirements.txt with `pip freeze > requirements.txt`
- Use type hints in function signatures
- Use f-strings for string formatting
- Use `pathlib.Path` instead of `os.path`
- Prefer `httpx` over `requests` for HTTP calls
- Use `async`/`await` for I/O-bound operations when appropriate
- Handle exceptions specifically, avoid bare `except:`
- Use `logging` module instead of `print()` for debugging in production code
- Follow PEP 8 naming: `snake_case` for functions/variables, `PascalCase` for classes
- Store secrets in `.env` file, load with `python-dotenv` (never commit .env)
- Use `pytest` for testing

## Project Structure

Preferred folder structure:
- `docs/` - documentation
- `tests/` - pytest tests
- `scripts/` - helper utilities and scripts
