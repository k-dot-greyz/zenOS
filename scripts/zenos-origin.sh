#!/usr/bin/env bash
# Owner-agnostic GitHub origin for template checkouts.
# Source from other scripts:  . "$(dirname "$0")/zenos-origin.sh"
# Curl-piped installers should inline the same logic — they cannot source this file.

zenos_github_owner() {
    if [[ -n "${ZENOS_GITHUB_OWNER:-}" ]]; then
        printf '%s' "$ZENOS_GITHUB_OWNER"
        return 0
    fi
    if [[ -n "${GITHUB_OWNER:-}" ]]; then
        printf '%s' "$GITHUB_OWNER"
        return 0
    fi
    if [[ -n "${GITHUB_USERNAME:-}" ]]; then
        printf '%s' "$GITHUB_USERNAME"
        return 0
    fi
    printf '%s' "YOUR_GITHUB_USERNAME"
}

zenos_github_clone_url() {
    local owner repo
    owner="$(zenos_github_owner)"
    repo="${ZENOS_REPO_NAME:-zenOS}"
    printf 'https://github.com/%s/%s.git' "$owner" "$repo"
}

zenos_github_raw_url() {
    local path="${1:?path required}"
    local owner repo branch
    owner="$(zenos_github_owner)"
    repo="${ZENOS_REPO_NAME:-zenOS}"
    branch="${ZENOS_REPO_BRANCH:-main}"
    printf 'https://raw.githubusercontent.com/%s/%s/%s/%s' "$owner" "$repo" "$branch" "$path"
}

zenos_require_github_owner() {
    local owner
    owner="$(zenos_github_owner)"
    if [[ -z "$owner" || "$owner" == "YOUR_GITHUB_USERNAME" ]]; then
        echo "No GitHub owner is baked into this template." >&2
        echo "Clone your fork and rerun from the checkout, or set ZENOS_GITHUB_OWNER." >&2
        return 1
    fi
    printf '%s' "$owner"
}
