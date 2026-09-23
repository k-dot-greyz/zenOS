#!/usr/bin/env bash
# ensure-python314.sh — install latest CPython 3.14.x (>= 3.14.7 floor) on PATH.
# Floor lives in pyproject.toml. This does not pin a patch (no 3.14.7-only install).
#
# Uses: gh + uv from GitHub Releases (host: release-assets.githubusercontent.com).
# Idempotent. Safe to re-run.
set -euo pipefail

MIN="${ENV_DOCTOR_PYTHON_MIN:-${ENV_DOCTOR_PYTHON_PIN:-3.14.7}}"
PREFIX="${PYTHON314_PREFIX:-${HOME}/.local}"
BIN_DIR="${PREFIX}/bin"
UV_BIN="${BIN_DIR}/uv"

_ver_ge() {
  local a="${1%%[!0-9.]*}" b="${2%%[!0-9.]*}"
  local a1 a2 a3 b1 b2 b3 rest
  IFS=. read -r a1 a2 a3 rest <<< "${a}.0.0"
  IFS=. read -r b1 b2 b3 rest <<< "${b}.0.0"
  a1=${a1:-0}; a2=${a2:-0}; a3=${a3:-0}
  b1=${b1:-0}; b2=${b2:-0}; b3=${b3:-0}
  a3=${a3%%[!0-9]*}; b3=${b3%%[!0-9]*}
  [[ -z "$a3" ]] && a3=0
  [[ -z "$b3" ]] && b3=0
  if (( 10#$a1 != 10#$b1 )); then
    if (( 10#$a1 > 10#$b1 )); then return 0; else return 1; fi
  fi
  if (( 10#$a2 != 10#$b2 )); then
    if (( 10#$a2 > 10#$b2 )); then return 0; else return 1; fi
  fi
  if (( 10#$a3 >= 10#$b3 )); then return 0; else return 1; fi
}

_python314_ok() {
  local py ver
  py="$(command -v python3.14 2>/dev/null || true)"
  [[ -z "$py" ]] && return 1
  ver="$("$py" --version 2>&1 | awk '{print $2}')"
  _ver_ge "$ver" "$MIN"
}

export PATH="${BIN_DIR}:${PATH}"

if _python314_ok; then
  echo "[ok] python3.14 $(python3.14 --version 2>&1 | awk '{print $2}') (>= ${MIN})"
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "[fail] gh CLI not found (needed to fetch uv from GitHub Releases)" >&2
  exit 1
fi

mkdir -p "$BIN_DIR"
arch="$(uname -m)"
case "$arch" in
  x86_64 | amd64) uv_asset="uv-x86_64-unknown-linux-gnu.tar.gz" ;;
  aarch64 | arm64) uv_asset="uv-aarch64-unknown-linux-gnu.tar.gz" ;;
  *)
    echo "[fail] unsupported arch ${arch}" >&2
    exit 1
    ;;
esac

if [[ ! -x "$UV_BIN" ]]; then
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  echo "[info] fetching ${uv_asset} from astral-sh/uv via gh"
  if ! gh release download --repo astral-sh/uv --pattern "$uv_asset" --clobber -D "$tmp"; then
    echo "[fail] cannot download uv. Allow Cloud egress for release-assets.githubusercontent.com (GitHub Release assets), then re-run." >&2
    exit 1
  fi
  tar -xzf "${tmp}/${uv_asset}" -C "$tmp"
  found="$(find "$tmp" -type f -name uv -perm -u+x | head -1)"
  if [[ -z "$found" ]]; then
    echo "[fail] uv binary missing from archive" >&2
    exit 1
  fi
  install -m 0755 "$found" "$UV_BIN"
  rm -rf "$tmp"
  trap - EXIT
fi

echo "[info] uv python install 3.14 (latest 3.14.x, not a patch pin)"
if ! "$UV_BIN" python install 3.14; then
  echo "[fail] uv python install 3.14 failed. Allow Cloud egress for release-assets.githubusercontent.com, then re-run." >&2
  exit 1
fi

py_path="$("$UV_BIN" python find 3.14)"
ln -sfn "$py_path" "${BIN_DIR}/python3.14"
# Do not clobber a system python3 — env-doctor prefers python3.14 on PATH.

if ! _python314_ok; then
  echo "[fail] python3.14 installed but below floor ${MIN}+" >&2
  python3.14 --version >&2 || true
  exit 1
fi

echo "[ok] python3.14 $(python3.14 --version 2>&1 | awk '{print $2}') (>= ${MIN})"
echo "[ok] PATH prefix: ${BIN_DIR}"
