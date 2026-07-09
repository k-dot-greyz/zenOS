#!/usr/bin/env bash
# hydrate.sh — scaffold local workspace from dev-master, zenOS-dev, or ducky templates

set -euo pipefail

DUCKY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZENOS_ROOT="$(cd "${DUCKY_ROOT}/.." && pwd)"
HYDRATION_DIR="${ZENOS_ROOT}/.zen-hydration"
PROFILE="${DUCKY_PROFILE:-developer}"
SOURCE_NAME="zenos-programmatic"
SOURCE_PATH=""

log() { printf '🦆 %s\n' "$*"; }

resolve_hydration_source() {
  if [[ -n "${ZEN_DEV_MASTER:-}" && -d "${ZEN_DEV_MASTER}/hydration" ]]; then
    SOURCE_NAME="dev-master"
    SOURCE_PATH="${ZEN_DEV_MASTER}/hydration"
    return 0
  fi

  for candidate in "${ZENOS_ROOT}/../dev-master" "${ZENOS_ROOT}/../../dev-master"; do
    if [[ -d "${candidate}/hydration" ]]; then
      SOURCE_NAME="dev-master"
      SOURCE_PATH="${candidate}/hydration"
      return 0
    fi
  done

  case "${PROFILE}" in
    mobile)
      SOURCE_PATH="${DUCKY_ROOT}/hydrate/mobile"
      ;;
    *)
      SOURCE_PATH="${DUCKY_ROOT}/hydrate/default"
      ;;
  esac
}

materialize_template() {
  local src="$1"
  local dest="$2"
  if [[ -e "${dest}" ]]; then
    log "skip (exists): ${dest#${ZENOS_ROOT}/}"
    return 0
  fi
  mkdir -p "$(dirname "${dest}")"
  if [[ -d "${src}" ]]; then
    cp -R "${src}" "${dest}"
  else
    cp "${src}" "${dest}"
  fi
  log "created: ${dest#${ZENOS_ROOT}/}"
}

hydrate_from_dir() {
  local template_dir="$1"
  if [[ ! -d "${template_dir}" ]]; then
    log "template dir missing: ${template_dir}"
    return 1
  fi

  while IFS= read -r -d '' file; do
    rel="${file#${template_dir}/}"
    dest_rel="${rel}"
    if [[ "${rel}" == "env.template" ]]; then
      dest_rel=".env"
    fi
    materialize_template "${file}" "${ZENOS_ROOT}/${dest_rel}"
  done < <(find "${template_dir}" -type f -print0)
}

write_manifest() {
  local timestamp
  timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  mkdir -p "${HYDRATION_DIR}"
  cat > "${HYDRATION_DIR}/manifest.json" <<EOF
{
  "schema": "zenos.ducky.hydration-manifest/v1",
  "hydrated_at": "${timestamp}",
  "profile": "${PROFILE}",
  "source": "${SOURCE_NAME}",
  "source_path": "${SOURCE_PATH}",
  "zenos_root": "${ZENOS_ROOT}"
}
EOF
  log "wrote manifest: .zen-hydration/manifest.json"
}

main() {
  log "hydration profile: ${PROFILE}"
  resolve_hydration_source
  log "hydration source: ${SOURCE_NAME} (${SOURCE_PATH})"
  hydrate_from_dir "${SOURCE_PATH}"
  write_manifest
}

main "$@"
