# Personal Claude Code Instructions

## Language

- **Communicate with user in Czech** (mluvíme česky)
- **Write all files in English** (code, comments, documentation, config files)
- Variable names, function names, commit messages - all in English

## Research

- **Use Perplexity MCP** before implementing any external API, library, or technology you haven't used in this project before
- When encountering errors or unexpected behavior - research first
- When deciding between approaches - research to find best practices

## General

- Do NOT use emoji in text output
- **ALWAYS use parallel sub-agents** (Task tool) when working on multiple independent tasks (writing tests, fixing files, implementing features). This is NOT optional - spawn one agent per task for maximum speed.
- For tasks with 3+ steps, **create a plan first** (use TodoWrite) and mark tasks as completed when done
- **Document in code comments**, not separate files. Create documentation files (README, docs/) only when explicitly requested
- **Write tests for all new code** - business logic, API endpoints, utilities. Skip only: config files, type definitions, trivial one-liners

- When exploring a feature or diagnosing a bug, always complete the full investigation and provide a summary of findings before stopping. Do not leave investigations half-done. If the task is large, break it into phases and complete at least phase 1 with actionable output.

## Implementation Integrity - No Mocks, No Skipping

- **NEVER create mock implementations** when real implementation is required
- **NEVER skip or stub out** functionality that is specified in the task or plan
- If something is in the plan/task, it MUST be fully implemented - no placeholders, no "TODO: implement later", no fake data
- If implementation is blocked, **ask the user** instead of silently mocking
- This applies to: API integrations, database operations, business logic, UI components - everything

```python
# BAD - mocking instead of implementing
def fetch_user_data(user_id):
    return {"id": user_id, "name": "Mock User"}  # NEVER DO THIS

# BAD - skipping with TODO
def process_payment(amount):
    # TODO: implement payment processing
    pass  # NEVER DO THIS

# GOOD - implement fully or ask for clarification
def fetch_user_data(user_id):
    response = httpx.get(f"{API_URL}/users/{user_id}")
    response.raise_for_status()
    return response.json()
```

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
- Do NOT include "🤖 Generated with Claude Code" footer in PR description
- Keep PR descriptions clean and focused on the changes

## Server Logging for Backtesting

- **All server applications MUST log** requests, responses, and key events for backtesting
- Logs go to `logs/` directory (gitignored, never committed)
- Use structured logging (JSON format preferred) for easy parsing
- Include: timestamps, request/response payloads, user actions, errors, performance metrics

```python
# Example logging setup
import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "app.log",
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    level=logging.INFO
)
```

## Browser Automation

- **Use Claude Chrome (MCP)** for all browser automation
- Use Playwright only when Claude Chrome is unavailable or something doesn't work in it

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
