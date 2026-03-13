# AGENTS.md

## Cursor Cloud specific instructions

### Overview

zenOS is a Python CLI tool for AI workflow orchestration. The primary product is the `zen` CLI (`zen/` package). There are also standalone prototypes (React Native mobile in `workspace/prototype/`, n8n integration in `n8n/`) that are not part of the core development workflow.

### Running the CLI

The `setup.py` in the repo root is a **custom setup orchestrator** (not a standard setuptools `setup.py`). This conflicts with `pip install -e .` because setuptools tries to execute it during the build. Workaround: install dependencies directly via pip and use `PYTHONPATH=/workspace` instead of editable install.

The CLI entry point (`zen.cli:main`) references a `main` function that doesn't exist in `cli.py` — the click group is named `cli`. Additionally, `zen/inbox.py` uses `@click.alias('inbox')` which is not a valid click API. To run the CLI programmatically, patch click first:

```python
import click
click.alias = lambda name: lambda func: func
from zen.cli import cli
cli(['plugins', 'list'], standalone_mode=False)
```

### Linting & Formatting

- **ruff**: `ruff check zen/` — many pre-existing warnings (4000+), but the tool runs correctly
- **black**: `black --check zen/` — most files need formatting; the tool runs
- **mypy**: `mypy zen/ --ignore-missing-imports` — the `pyproject.toml` sets `python_version = "3.8"` which mypy >= 1.19 doesn't support; override with `--python-version 3.9` or ignore

### Tests

No `tests/` directory exists. The `pyproject.toml` configures pytest with `testpaths = ["tests"]` but no tests have been written yet.

### External API

zenOS uses OpenRouter API (`openrouter.ai`) for LLM calls. Set `OPENROUTER_API_KEY` as an environment variable or in `.env`. In cloud environments with restricted egress, API calls will fail with connection reset — this is expected.

### Key caveats

- PostgreSQL and Redis are defined in `docker-compose.yml` but are **not wired into** the Python source code — no DB client libraries are imported. They can be ignored for development.
- The `requirements.txt` lists some stdlib modules (asyncio, threading, etc.) that will cause pip errors — use `pyproject.toml` as the canonical dependency source.
- Extra runtime deps not in `pyproject.toml` but needed: `aiofiles`, `psutil`, `textblob`, `nltk`.
