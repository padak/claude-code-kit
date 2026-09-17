---
paths:
  - "**/*.py"
  - "pyproject.toml"
  - "uv.lock"
---

# Python

- Use `uv` for everything: `uv init`, `uv add <pkg>`, `uv run <cmd>`. Dependencies live in `pyproject.toml` with `uv.lock` committed. No `pip install`, no `requirements.txt`, no manual venv.
- `httpx` over `requests`, `pathlib.Path` over `os.path`, `logging` over `print`, f-strings for formatting.
- Type hints on function signatures. `async`/`await` for I/O-bound work when it fits.
- Catch specific exceptions, never bare `except:`.
- Secrets come from `.env` via `python-dotenv`. `.env` is gitignored.
- Tests with `pytest` in `tests/`. Helper scripts in `scripts/`. Docs, when requested, in `docs/`.
