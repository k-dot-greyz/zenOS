#!/usr/bin/env bash
# Compatibility shim. Canonical file lives under dex/<bank>/scripts/<lang>/.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
TARGET="$ROOT/dex/ops/scripts/termux-bash/termux-install.sh"
if [ ! -f "$TARGET" ]; then
  echo "canonical script missing: $TARGET" >&2
  exit 1
fi
exec bash "$TARGET" "$@"
