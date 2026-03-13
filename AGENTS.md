# AGENTS.md

## Cursor Cloud specific instructions

### Overview

zenOS is a Python CLI tool for AI workflow orchestration. The core package is `zen/` with entry point `zen.cli:main`. See `README.md` for full product description and `docs/guides/` for platform-specific setup guides.

### Virtual Environment

The project uses a Python venv at `.venv/`. Always activate it before running anything:

```bash
source .venv/bin/activate
```

### Known Issues

- **`zen` CLI entry point crashes on import** due to `@click.alias('inbox')` in `zen/inbox.py` line 95. `click.alias` does not exist in any version of Click. The core library (`zen.core`, `zen.agents`, `zen.plugins`, `zen.pkm`, etc.) works fine — only the CLI entry point (`zen.cli`) is affected. To test core functionality, import modules directly via Python rather than using the `zen` command.
- **`zen/core/context.py`** has a SyntaxError (f-string with embedded quotes) that prevents it from being imported/parsed. This doesn't block most tests.
- **`setup.py`** is NOT a standard setuptools script — it's a custom CLI tool that calls `zen.setup.unified_setup.main()`. This conflicts with `pip install -e .` because setuptools tries to execute it. Workaround: temporarily rename `setup.py` before running `pip install -e .`, then rename it back.

### Lint / Test / Build

| Task | Command |
|------|---------|
| Lint (format check) | `black --check .` |
| Lint (ruff) | `ruff check .` |
| Lint (flake8 errors only) | `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` |
| Run tests | `pytest` |
| Custom test runner | `python test_runner.py` |
| Import check | `python -c "import zen; print(zen.__version__)"` |

The CI workflow (`.github/workflows/python-app.yml`) also runs `isort --check-only .`, `mypy .`, `bandit -r .`, and `pytest --cov`. These have `continue-on-error: true` on some steps.

### Dependencies

Core deps are in `pyproject.toml` `[project.dependencies]`. Dev deps are in `[project.optional-dependencies.dev]`. The `requirements.txt` has optional/TTS dependencies and is NOT the main dependency file.

Undeclared runtime dependencies that are imported but not listed in `pyproject.toml`: `aiofiles`, `psutil`. These must be installed separately.

### Services

- **PostgreSQL / Redis**: Optional, only needed for Docker-based deployment (`docker-compose.yml`). Not required for local dev or testing.
- **OpenRouter API**: Required for AI features (`OPENROUTER_API_KEY` env var). Not required for running tests or core library imports.
