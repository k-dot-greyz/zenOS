#!/usr/bin/env bash
# Central origin for template checkouts. Source from other scripts:
#   . "$(dirname "$0")/zenos-origin.sh"
# Reads, in order: process env, .env (cwd then repo root), git remote origin.
# Curl-piped installers should source this only when it exists on disk.

_zenos_trim() {
    local value="${1-}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    value="${value#\"}"
    value="${value%\"}"
    value="${value#\'}"
    value="${value%\'}"
    printf '%s' "$value"
}

_zenos_is_placeholder() {
    local value
    value="$(_zenos_trim "${1-}")"
    case "$value" in
        ""|"YOUR_GITHUB_USERNAME"|"YOUR_GITHUB_OWNER"|"<owner>"|"OWNER") return 0 ;;
        *) return 1 ;;
    esac
}

_zenos_is_placeholder_secret() {
    local value
    value="$(_zenos_trim "${1-}")"
    case "$value" in
        ""|"your-api-key-here"|"sk-or-v1-your-api-key-here"|"YOUR_API_KEY"|"<your-api-key>"|"changeme"|"your_token_here"|"your_personal_access_token")
            return 0
            ;;
        *) return 1 ;;
    esac
}

_zenos_load_dotenv() {
    local file="$1"
    [[ -f "$file" ]] || return 0
    local line key value
    while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%"${line##*[![:space:]]}"}"
        [[ -z "$line" || "$line" == \#* ]] && continue
        [[ "$line" == *=* ]] || continue
        key="${line%%=*}"
        value="${line#*=}"
        key="$(_zenos_trim "$key")"
        value="$(_zenos_trim "$value")"
        [[ -z "$key" ]] && continue
        # Don't clobber process env
        if [[ -z "${!key:-}" ]]; then
            export "$key=$value"
        fi
    done < "$file"
}

zenos_load_dotenv() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    _zenos_load_dotenv ".env"
    _zenos_load_dotenv "$script_dir/../.env"
}

_zenos_parse_github_remote() {
    local url="$1"
    local rest owner repo
    url="$(_zenos_trim "$url")"
    [[ -z "$url" ]] && return 1
    if [[ "$url" =~ ^https?://([^@]+@)?(www\.)?github\.com/([^/]+)/([^/]+) ]]; then
        owner="${BASH_REMATCH[3]}"
        repo="${BASH_REMATCH[4]}"
    elif [[ "$url" =~ ^git@github\.com:([^/]+)/([^/]+) ]]; then
        owner="${BASH_REMATCH[1]}"
        repo="${BASH_REMATCH[2]}"
    elif [[ "$url" =~ ^ssh://git@github\.com/([^/]+)/([^/]+) ]]; then
        owner="${BASH_REMATCH[1]}"
        repo="${BASH_REMATCH[2]}"
    else
        return 1
    fi
    repo="${repo%.git}"
    repo="${repo%/}"
    if _zenos_is_placeholder "$owner"; then
        return 1
    fi
    printf '%s %s' "$owner" "$repo"
}

zenos_git_remote() {
    git remote get-url origin 2>/dev/null || true
}

zenos_github_owner() {
    zenos_load_dotenv
    local owner parsed
    owner="$(_zenos_trim "${ZENOS_GITHUB_OWNER:-${GITHUB_OWNER:-${GITHUB_USERNAME:-}}}")"
    if ! _zenos_is_placeholder "$owner"; then
        printf '%s' "$owner"
        return 0
    fi
    parsed="$(_zenos_parse_github_remote "${ZENOS_REPO_URL:-}")"
    if [[ -n "$parsed" ]]; then
        printf '%s' "${parsed%% *}"
        return 0
    fi
    parsed="$(_zenos_parse_github_remote "$(zenos_git_remote)")"
    if [[ -n "$parsed" ]]; then
        printf '%s' "${parsed%% *}"
        return 0
    fi
    printf '%s' "YOUR_GITHUB_USERNAME"
}

zenos_github_repo() {
    zenos_load_dotenv
    local parsed repo
    parsed="$(_zenos_parse_github_remote "${ZENOS_REPO_URL:-}")"
    if [[ -n "$parsed" ]]; then
        printf '%s' "${parsed##* }"
        return 0
    fi
    repo="$(_zenos_trim "${ZENOS_REPO_NAME:-}")"
    if [[ -n "$repo" ]]; then
        printf '%s' "$repo"
        return 0
    fi
    parsed="$(_zenos_parse_github_remote "$(zenos_git_remote)")"
    if [[ -n "$parsed" ]]; then
        printf '%s' "${parsed##* }"
        return 0
    fi
    printf '%s' "zenOS"
}

zenos_github_clone_url() {
    local owner repo url parsed
    zenos_load_dotenv
    url="$(_zenos_trim "${ZENOS_REPO_URL:-}")"
    parsed="$(_zenos_parse_github_remote "$url")"
    if [[ -n "$parsed" ]]; then
        owner="${parsed%% *}"
        repo="${parsed##* }"
        printf 'https://github.com/%s/%s.git' "$owner" "$repo"
        return 0
    fi
    owner="$(zenos_github_owner)"
    repo="$(zenos_github_repo)"
    if _zenos_is_placeholder "$owner"; then
        return 1
    fi
    printf 'https://github.com/%s/%s.git' "$owner" "$repo"
}

zenos_github_raw_url() {
    local path="${1:?path required}"
    local owner repo branch
    owner="$(zenos_github_owner)"
    repo="$(zenos_github_repo)"
    branch="${ZENOS_REPO_BRANCH:-main}"
    if _zenos_is_placeholder "$owner"; then
        return 1
    fi
    printf 'https://raw.githubusercontent.com/%s/%s/%s/%s' "$owner" "$repo" "$branch" "$path"
}

zenos_require_github_owner() {
    local owner
    owner="$(zenos_github_owner)"
    if _zenos_is_placeholder "$owner"; then
        echo "GitHub origin is not configured." >&2
        echo "Set ZENOS_GITHUB_OWNER (or ZENOS_REPO_URL) in .env, or clone this repo so origin exists." >&2
        return 1
    fi
    printf '%s' "$owner"
}

zenos_openrouter_key() {
    local key
    zenos_load_dotenv
    key="$(_zenos_trim "${OPENROUTER_API_KEY:-}")"
    if _zenos_is_placeholder_secret "$key"; then
        return 1
    fi
    printf '%s' "$key"
}

zenos_github_token() {
    local token
    zenos_load_dotenv
    token="$(_zenos_trim "${GITHUB_TOKEN:-}")"
    if _zenos_is_placeholder_secret "$token"; then
        return 1
    fi
    printf '%s' "$token"
}

zenos_require_openrouter_key() {
    if zenos_openrouter_key >/dev/null; then
        return 0
    fi
    echo "OPENROUTER_API_KEY is not set." >&2
    echo "Set it once in .env (copy env.example) or export it in the environment." >&2
    echo "Get a key at: https://openrouter.ai/keys" >&2
    return 1
}

zenos_set_dotenv_value() {
    local key="${1:?key required}"
    local value="${2-}"
    local file="${3:-.env}"
    local tmp
    tmp="$(mktemp)"
    if [[ -f "$file" ]]; then
        awk -v k="$key" -v v="$value" '
            BEGIN { done = 0 }
            index($0, k "=") == 1 {
                print k "=" v
                done = 1
                next
            }
            { print }
            END { if (!done) print k "=" v }
        ' "$file" > "$tmp"
        mv "$tmp" "$file"
    else
        printf '%s=%s\n' "$key" "$value" > "$file"
    fi
    export "$key=$value"
}
