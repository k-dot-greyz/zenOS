#!/usr/bin/env bash
# ducky/run.sh — tap-to-bootstrap entry for USB drives and Termux
#
# Usage:
#   bash ducky/run.sh                  # default developer profile
#   DUCKY_PROFILE=mobile bash ducky/run.sh
#   bash /storage/emulated/0/ducky/run.sh   # from USB / shared storage on Android

set -euo pipefail

DUCKY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZENOS_ROOT="$(cd "${DUCKY_ROOT}/.." && pwd)"
PROFILE="${DUCKY_PROFILE:-developer}"

log() { printf '🦆 %s\n' "$*"; }
warn() { printf '⚠️  %s\n' "$*" >&2; }

detect_termux() {
  [[ -n "${TERMUX_VERSION:-}" || -d /data/data/com.termux ]]
}

termux_bootstrap() {
  if ! detect_termux; then
    return 0
  fi
  log "Termux detected — ensuring storage + wake lock"
  if command -v termux-setup-storage >/dev/null 2>&1; then
    termux-setup-storage >/dev/null 2>&1 || true
  fi
  if command -v termux-wake-lock >/dev/null 2>&1; then
    termux-wake-lock || true
  fi
}

run_env_doctor() {
  log "running env-doctor"
  python3 "${DUCKY_ROOT}/env_doctor.py" --zenos-root "${ZENOS_ROOT}" || {
    warn "env-doctor reported issues — continuing hydration"
    return 0
  }
}

run_hydration() {
  log "hydrating scaffold (profile=${PROFILE})"
  DUCKY_PROFILE="${PROFILE}" bash "${DUCKY_ROOT}/hydrate.sh"
}

run_programmatic_setup() {
  if [[ ! -f "${ZENOS_ROOT}/setup.py" ]]; then
    warn "setup.py not found — clone zenOS into ${ZENOS_ROOT} first"
    return 1
  fi

  case "${PROFILE}" in
    minimal)
      log "running programmatic setup: validate-only"
      (cd "${ZENOS_ROOT}" && python3 setup.py --validate-only) || true
      ;;
    offline)
      log "running offline setup hooks"
      if [[ -x "${ZENOS_ROOT}/scripts/setup-offline.sh" ]]; then
        bash "${ZENOS_ROOT}/scripts/setup-offline.sh"
      else
        warn "scripts/setup-offline.sh not found"
      fi
      ;;
    *)
      log "running programmatic setup: unattended"
      (cd "${ZENOS_ROOT}" && python3 setup.py --unattended) || {
        warn "unattended setup had issues — run python setup.py manually"
        return 0
      }
      ;;
  esac
}

main() {
  log "ducky quickstart — zenOS env pipeline"
  log "zenOS root: ${ZENOS_ROOT}"
  termux_bootstrap
  run_env_doctor
  run_hydration
  run_programmatic_setup
  log "done — check .zen-hydration/ for local deets + manifest"
  log "next: zen doctor --ai-mode  (or python -m zen.cli_v2 doctor --ai-mode)"
}

main "$@"
