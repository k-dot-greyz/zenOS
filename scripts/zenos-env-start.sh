#!/usr/bin/env bash
# zenOS per-boot start gate: fail the environment if Python < 3.14 or core deps are missing.
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${ZEN_PYTHON:-}"
if [ -z "$PY" ] && [ -x "$ROOT/.venv/bin/python" ]; then
  PY="$ROOT/.venv/bin/python"
fi
if [ -z "$PY" ]; then
  PY="$(command -v python3.14 || true)"
fi
if [ -z "$PY" ] || [ ! -x "$PY" ]; then
  echo "zenOS start: Python 3.14+ interpreter not found (.venv/bin/python or python3.14)." >&2
  exit 1
fi

"$PY" - <<'PY'
import sys

if sys.version_info[:2] < (3, 14):
    print(
        f"zenOS start requires Python 3.14+, got {sys.version.split()[0]}",
        file=sys.stderr,
    )
    raise SystemExit(1)

try:
    from zen.runtime import require_runtime
except ImportError as exc:
    print(
        f"zenOS start: cannot import zen.runtime ({exc}). "
        "Install with: uv pip install --python .venv -e .",
        file=sys.stderr,
    )
    raise SystemExit(1)

require_runtime()
print(f"zenOS start: runtime OK ({sys.version.split()[0]})")
PY
