#!/usr/bin/env bash
# Mirror zenOS .cursor/skills → ~/.cursor/skills
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash -c '
  SRC="$1/.cursor/skills"
  DEST="${CURSOR_SKILLS_HOME:-$HOME/.cursor/skills}"
  mkdir -p "$DEST"
  for d in "$SRC"/*/; do
    [[ -d "$d" ]] || continue
    name=$(basename "$d")
    rsync -a --delete "$d" "$DEST/$name/"
    echo "synced: $name"
  done
  [[ -f "$SRC/README.md" ]] && cp "$SRC/README.md" "$DEST/../skills-zenOS-README.md" 2>/dev/null || true
' _ "$ROOT"
