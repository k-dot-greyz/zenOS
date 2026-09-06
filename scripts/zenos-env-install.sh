#!/usr/bin/env bash
# zenOS Cloud / local install: CPython 3.14+ venv and current stable deps.
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "zenOS install: Python 3.14+ required"

if ! command -v uv >/dev/null 2>&1; then
  echo "zenOS install: uv is required but was not found in PATH." >&2
  echo "Install uv from https://docs.astral.sh/uv/getting-started/installation/ and re-run this script." >&2
  exit 1
fi

uv python install 3.14

if [ -x .venv/bin/python ] && .venv/bin/python -c "import sys; raise SystemExit(0 if sys.version_info[:2] >= (3, 14) else 1)"; then
  echo "zenOS install: reusing existing 3.14 venv"
else
  uv venv --python 3.14 --seed --clear .venv
fi

# Root setup.py is now a PEP 517-safe shim (setuptools.setup() during the
# build hook, wizard only for `python setup.py [wizard flags]`) — no longer
# needs to be renamed out of the way before an editable install.
uv pip install --python .venv -e ".[dev]"

if [ ! -f .env ] && [ -f env.example ]; then
  cp env.example .env
fi

.venv/bin/python -c "from zen.runtime import require_runtime; require_runtime()"
echo "zenOS install: runtime OK ($(".venv/bin/python" -c 'import sys; print(sys.version.split()[0])'))"
