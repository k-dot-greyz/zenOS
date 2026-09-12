# Review and merge

Guiding story: you open a PR, CI tells you what is broken, and a human (or an
agent that remembers this file) knows which comments to fix versus which to
push back on.

## Merge-blocking

These have to be green. Everything else is noise until they are.

1. **Black on CPython 3.14.** PEP 758 `except E1, E2` without parens is valid
   3.14 and **SyntaxError** on 3.12. Format with:

   ```bash
   uvx --python 3.14 black .
   ```

   `black --fast` on 3.12 will "fix" that syntax into something 3.14 does not
   want. Do not do that.

2. **Identity scanner.** Template-friendly repo: no baked-in GitHub user,
   personal paths, or Gemini share links.

   ```bash
   python scripts/check_no_identity_leaks.py
   ```

3. **Tests.** Root `setup.py` is an installer, not setuptools. Park it, install,
   restore, then run pytest **without** the pyproject `addopts` coverage hook
   (that needs pytest-cov on the PATH):

   ```bash
   mv setup.py _setup.py.bak
   pip install -e ".[dev]"
   mv _setup.py.bak setup.py
   pytest tests/ -o addopts=
   ```

CI (`.github/workflows/zenos-ci.yml`) runs lint, identity, and tests in
parallel. Security, ShellCheck, and docs jobs are **informational**. They do
not gate merge.

Required GitHub checks to pin in branch protection: **Lint & Format Check**,
**Python Tests**, **Identity leak scanner** (or the **CI Status Check** job
that wraps those three).

## Push back

Do not treat these as merge blockers:

- **80% docstring coverage.** CodeRabbit's docstring pre-merge check is off
  in `.coderabbit.yaml`. We do not write essay-length docstrings to satisfy a
  percentage.
- **Checksums / signing of unsigned `curl | bash` blobs.** Installers prefer a
  local checkout. Signing theater on unsigned raw GitHub blobs is not a
  release process.
- **Checklist theater.** "Benchmarked for performance", "highlighted code
  replaced", "dependencies are up to date" — gone from the PR template. If a
  bot resurrects them, ignore it.
- **Archive / inbox functional nits.** `docs/archive/**` and `inbox/**` get
  identity review only.

## Agents

- Format with `uvx --python 3.14 black .`, then isort if you touched imports.
- Reply on CodeRabbit / human review **threads**. Do **not** resolve them; the
  author does that.
- CodeRabbit is suggestions, not orders. If a comment fights this file, say so
  on the thread and skip the change.
- PR body: intent, how to verify, origin/`.env` impact, what was intentionally
  skipped, `Closes #`.

## CodeRabbit

Repo config: `.coderabbit.yaml`.

- Docstring coverage: **off**.
- Installers and `zen/origin.py`: functional review. Empty and placeholder
  origin keys count as unset. Do not demand signed releases.
- `docs/archive/**` and `inbox/**`: identity-only; path filters skip them from
  the main review pass where possible.
