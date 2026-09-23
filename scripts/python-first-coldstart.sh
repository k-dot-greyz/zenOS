#!/usr/bin/env bash
# python-first-coldstart.sh — CPython 3.14.7+ FIRST, then pip, then optional npm.
# Do not probe the marketing package. Do not ignore requires-python. .[dev] only.
#
# Usage:
#   bash scripts/python-first-coldstart.sh [REPO_ROOT]
#
# Exit 2 = FLOOR_UNMET (do not pip into an older interpreter).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ $# -ge 1 && -n "${1:-}" && "${1#-}" = "$1" ]]; then
  REPO_ROOT="$(cd "$1" && pwd)"
elif [[ -f "$SCRIPT_DIR/../pyproject.toml" ]]; then
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
  REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
fi
cd "$REPO_ROOT"
export PATH="${HOME}/.local/bin:${PATH}"

ENSURE="${SCRIPT_DIR}/ensure-python314.sh"
if [[ ! -x "$ENSURE" && -f "$ENSURE" ]]; then
  chmod +x "$ENSURE" || true
fi
if [[ ! -f "$ENSURE" ]]; then
  echo "FLOOR_UNMET: ensure-python314.sh missing" >&2
  exit 2
fi

if ! bash "$ENSURE"; then
  echo "FLOOR_UNMET: python3.14 >= 3.14.7 required before pip/npm" >&2
  exit 2
fi

PY="$(command -v python3.14)"
if [[ -z "$PY" ]]; then
  echo "FLOOR_UNMET: python3.14 not on PATH after ensure" >&2
  exit 2
fi

if [[ -x .venv/bin/python ]]; then
  if ! .venv/bin/python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 14, 7) else 1)"; then
    echo "[info] dropping stale venv (< 3.14.7) to avoid wheel collisions" >&2
    rm -rf .venv
  fi
fi

if [[ ! -x .venv/bin/python ]]; then
  echo "[info] creating .venv with $PY" >&2
  "$PY" -m venv .venv
fi

# Root setup.py is a zenOS installer script, not setuptools. Move it aside for pip -e.
restore_setup() {
  if [[ -f _setup.py.bak ]]; then
    mv _setup.py.bak setup.py
  fi
}
if [[ -f setup.py ]]; then
  mv setup.py _setup.py.bak
  trap restore_setup EXIT
fi

.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -e ".[dev]"
restore_setup
trap - EXIT

if command -v npm >/dev/null 2>&1; then
  if ! npm install -g npm@latest >/dev/null 2>&1; then
    echo "[warn] npm CLI upgrade skipped (node too old or no write access)" >&2
  fi
fi

echo "[ok] python-first coldstart: $($PY --version) + .[dev]"
