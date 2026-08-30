#!/usr/bin/env bash
# zenOS Cloud / local install: CPython 3.14+ venv and current stable deps.
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "zenOS install: Python 3.14+ required"

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

uv python install 3.14

if [ -x .venv/bin/python ] && .venv/bin/python -c "import sys; raise SystemExit(0 if sys.version_info[:2] >= (3, 14) else 1)"; then
  echo "zenOS install: reusing existing 3.14 venv"
else
  uv venv --python 3.14 --seed --clear .venv
fi

# Root setup.py is a zenOS installer script, not setuptools.
if [ -f setup.py ]; then
  mv setup.py _setup.py.bak
fi
uv pip install --python .venv -e ".[dev]"
if [ -f _setup.py.bak ]; then
  mv _setup.py.bak setup.py
fi

if [ ! -f .env ] && [ -f env.example ]; then
  cp env.example .env
fi

.venv/bin/python -c "from zen.runtime import require_runtime; require_runtime()"
echo "zenOS install: runtime OK ($(".venv/bin/python" -c 'import sys; print(sys.version.split()[0])'))"
