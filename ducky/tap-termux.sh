#!/data/data/com.termux/files/usr/bin/bash
# tap-termux.sh — Termux home-screen widget / shortcut target
# Point your Termux:Widget shortcut at this script after copying ducky to storage.

set -euo pipefail

# Common mount points when ducky lives on shared storage or USB OTG
CANDIDATES=(
  "${HOME}/storage/shared/ducky/run.sh"
  "${HOME}/storage/downloads/ducky/run.sh"
  "${HOME}/storage/documents/ducky/run.sh"
  "${HOME}/zenOS/ducky/run.sh"
  "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run.sh"
)

for candidate in "${CANDIDATES[@]}"; do
  if [[ -f "${candidate}" ]]; then
    export DUCKY_PROFILE="${DUCKY_PROFILE:-mobile}"
    exec bash "${candidate}"
  fi
done

echo "🦆 ducky not found. Copy zenOS (with ducky/) to one of:"
printf '  - %s\n' "${CANDIDATES[@]}"
exit 1
