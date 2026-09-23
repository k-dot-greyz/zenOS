#!/usr/bin/env bash
# zenOS per-boot start: cwd-proof. Heal via python-first if the venv is stale.
# Do not ignore requires-python. Do not pip into 3.12.
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

_healthy() {
  local py="$1"
  [[ -x "$py" ]] || return 1
  "$py" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 14, 7) else 1)" >/dev/null 2>&1 || return 1
  "$py" -c "import click, rich, yaml" >/dev/null 2>&1
}

PY="${ZEN_PYTHON:-}"
if [[ -z "$PY" && -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
fi
if [[ -z "$PY" ]]; then
  PY="$(command -v python3.14 || true)"
fi

if [[ -z "${PY}" || ! -x "$PY" ]] || ! _healthy "$PY"; then
  echo "zenOS start: floor unmet — running python-first-coldstart" >&2
  if ! bash "$ROOT/scripts/python-first-coldstart.sh" "$ROOT"; then
    echo "FLOOR_UNMET: python3.14 >= 3.14.7 required" >&2
    exit 2
  fi
  PY="$ROOT/.venv/bin/python"
fi

"$PY" - <<'PY'
import sys

if sys.version_info < (3, 14, 7):
    print(
        f"zenOS start requires Python 3.14.7+, got {sys.version.split()[0]}",
        file=sys.stderr,
    )
    raise SystemExit(2)

try:
    from zen.runtime import require_runtime
except ImportError as exc:
    print(
        f"zenOS start: cannot load zen.runtime ({exc}). "
        "Install with: bash scripts/python-first-coldstart.sh",
        file=sys.stderr,
    )
    raise SystemExit(1)

require_runtime()
print(f"zenOS start: runtime OK ({sys.version.split()[0]})")
PY
