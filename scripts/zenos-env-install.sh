#!/usr/bin/env bash
# zenOS Cloud / local install: Python 3.14.7+ FIRST, then pip, then optional npm.
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! bash "$ROOT/scripts/python-first-coldstart.sh" "$ROOT"; then
  echo "FLOOR_UNMET: python3.14 >= 3.14.7 required before pip" >&2
  exit 2
fi

if [[ ! -f .env && -f env.example ]]; then
  cp env.example .env
fi

echo "zenOS install: python-first OK"
