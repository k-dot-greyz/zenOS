"""Central origin + secrets for template-friendly zenOS checkouts.

Set identity and API keys once in `.env` (copy `env.example`). Runtime
also reads `git remote get-url origin`, so a normal clone of your fork
already knows the owner/repo — no baked-in GitHub username.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

REPO_NAME = "zenOS"
PLACEHOLDER_OWNER = "YOUR_GITHUB_USERNAME"
DEFAULT_HTTP_REFERER = "https://zenos.ai"
DEFAULT_BRANCH = "main"

_GITHUB_HTTPS = re.compile(
    r"^https?://(?:[^@\s]+@)?(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)
_GITHUB_SSH = re.compile(
    r"^(?:ssh://)?git@github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)

_DETECT = object()
_PLACEHOLDERS = frozenset(
    {
        "",
        PLACEHOLDER_OWNER,
        "YOUR_GITHUB_OWNER",
        "<owner>",
        "OWNER",
    }
)

_SECRET_PLACEHOLDERS = frozenset(
    {
        "",
        "your-api-key-here",
        "sk-or-v1-your-api-key-here",
        "YOUR_API_KEY",
        "<your-api-key>",
        "changeme",
        "your_token_here",
        "your_personal_access_token",
    }
)


@dataclass(frozen=True)
class Origin:
    """Resolved GitHub origin + shared secrets."""

    owner: str
    repo: str
    branch: str
    http_referer: str
    clone_url: Optional[str]
    web_url: Optional[str]
    raw_base: Optional[str]
    private_repo: Optional[str]
    openrouter_api_key: Optional[str]
    github_token: Optional[str]
    configured: bool
    source: str

    def require_clone_url(self) -> str:
        if not self.clone_url:
            raise ValueError(
                "GitHub origin is not configured. Set ZENOS_GITHUB_OWNER / "
                "ZENOS_REPO_URL in .env, or clone this repo so git remote origin exists."
            )
        return self.clone_url


def parse_github_remote(url: Optional[str]) -> Optional[tuple[str, str]]:
    """Parse owner/repo from a GitHub HTTPS or SSH remote. Ignore placeholders."""
    if not url:
        return None
    text = url.strip()
    match = _GITHUB_HTTPS.match(text) or _GITHUB_SSH.match(text)
    if not match:
        return None
    owner, repo = match.group(1), match.group(2)
    if _is_placeholder(owner):
        return None
    return owner, repo


def _is_placeholder(value: Optional[str]) -> bool:
    if value is None:
        return True
    return value.strip() in _PLACEHOLDERS


def is_configured_secret(value: Optional[str]) -> bool:
    """True when a key/token is present and not a documented placeholder."""
    cleaned = _clean(value)
    if cleaned is None:
        return False
    return cleaned not in _SECRET_PLACEHOLDERS


def _secret(value: Optional[str]) -> Optional[str]:
    return value if is_configured_secret(value) else None


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip().strip("'").strip('"')
    return stripped or None


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key or key.startswith("#"):
            continue
        data[key] = value.strip().strip("'").strip('"')
    return data


def detect_git_remote(root: Optional[Path] = None) -> Optional[str]:
    """Return `origin` URL for this checkout, if git is available."""
    cwd = str(root) if root is not None else None
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    return url or None


def _lookup(environ: Mapping[str, str], dotenv: Mapping[str, str], key: str) -> Optional[str]:
    for source in (environ, dotenv):
        value = _clean(source.get(key))
        if value:
            return value
    return None


def resolve(
    *,
    root: Optional[Path] = None,
    environ: Optional[Mapping[str, str]] = None,
    dotenv_path: Optional[Path] = None,
    git_remote: Optional[str] | object = _DETECT,
) -> Origin:
    """Resolve origin from env, `.env`, then git remote. First configured source wins."""
    explicit_root = root is not None
    repo_root = Path(root) if explicit_root else Path(__file__).resolve().parents[1]
    env = environ if environ is not None else os.environ
    if dotenv_path is not None:
        dotenv = _read_dotenv(dotenv_path)
    elif explicit_root:
        dotenv = _read_dotenv(repo_root / ".env")
    else:
        dotenv = {}
        for path in (Path.cwd() / ".env", repo_root / ".env"):
            for key, value in _read_dotenv(path).items():
                dotenv.setdefault(key, value)

    env_url = _clean(env.get("ZENOS_REPO_URL"))
    dotenv_url = _clean(dotenv.get("ZENOS_REPO_URL"))
    env_owner = (
        _clean(env.get("ZENOS_GITHUB_OWNER"))
        or _clean(env.get("GITHUB_OWNER"))
        or _clean(env.get("GITHUB_USERNAME"))
    )
    dotenv_owner = (
        _clean(dotenv.get("ZENOS_GITHUB_OWNER"))
        or _clean(dotenv.get("GITHUB_OWNER"))
        or _clean(dotenv.get("GITHUB_USERNAME"))
    )
    repo = _clean(env.get("ZENOS_REPO_NAME")) or _clean(dotenv.get("ZENOS_REPO_NAME")) or REPO_NAME
    owner: Optional[str] = None
    source = "unset"
    explicit_url = env_url or dotenv_url

    parsed_env_url = parse_github_remote(env_url)
    parsed_dotenv_url = parse_github_remote(dotenv_url)
    if parsed_env_url:
        owner, repo = parsed_env_url
        source = "repo_url"
    elif env_owner and not _is_placeholder(env_owner):
        owner = env_owner
        source = "environ"
    elif parsed_dotenv_url:
        owner, repo = parsed_dotenv_url
        source = "repo_url"
    elif dotenv_owner and not _is_placeholder(dotenv_owner):
        owner = dotenv_owner
        source = "dotenv"

    if _is_placeholder(owner):
        if git_remote is _DETECT:
            remote = detect_git_remote(Path.cwd()) or detect_git_remote(repo_root)
        else:
            remote = git_remote  # type: ignore[assignment]
        parsed_remote = parse_github_remote(remote)
        if parsed_remote:
            owner, repo = parsed_remote
            source = "git_remote"
            if not explicit_url:
                explicit_url = remote

    configured = not _is_placeholder(owner)
    owner = owner if configured else PLACEHOLDER_OWNER
    branch = _lookup(env, dotenv, "ZENOS_REPO_BRANCH") or DEFAULT_BRANCH
    referer = (
        _lookup(env, dotenv, "ZENOS_HTTP_REFERER")
        or _lookup(env, dotenv, "ZENOS_APP_URL")
        or DEFAULT_HTTP_REFERER
    )
    clone_url = None
    web_url = None
    raw_base = None
    if configured:
        clone_url = (
            explicit_url
            if explicit_url and explicit_url.endswith(".git")
            else (f"https://github.com/{owner}/{repo}.git")
        )
        # Prefer canonical HTTPS clone URL when we parsed GitHub owner/repo
        if parse_github_remote(clone_url):
            clone_url = f"https://github.com/{owner}/{repo}.git"
        web_url = f"https://github.com/{owner}/{repo}"
        raw_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}"

    private_repo = _lookup(env, dotenv, "ZENOS_PRIVATE_REPO")
    if not private_repo and configured:
        private_repo = f"https://github.com/{owner}/{repo}-dev.git"

    return Origin(
        owner=owner,
        repo=repo,
        branch=branch,
        http_referer=referer,
        clone_url=clone_url,
        web_url=web_url,
        raw_base=raw_base,
        private_repo=private_repo,
        openrouter_api_key=_secret(_lookup(env, dotenv, "OPENROUTER_API_KEY")),
        github_token=_secret(_lookup(env, dotenv, "GITHUB_TOKEN")),
        configured=configured,
        source=source if configured else "unset",
    )


def _default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def github_owner() -> str:
    return resolve().owner


def github_repo_url(*, git: bool = True, repo: str = REPO_NAME) -> str:
    origin = resolve()
    if origin.configured:
        if git:
            return origin.clone_url or f"https://github.com/{origin.owner}/{origin.repo}.git"
        return origin.web_url or f"https://github.com/{origin.owner}/{origin.repo}"
    # Unconfigured: keep a documentable shape, never a person
    suffix = ".git" if git else ""
    return f"https://github.com/{PLACEHOLDER_OWNER}/{repo}{suffix}"


def github_raw_url(path: str, *, branch: str = DEFAULT_BRANCH, repo: str = REPO_NAME) -> str:
    origin = resolve()
    owner = origin.owner if origin.configured else PLACEHOLDER_OWNER
    used_repo = origin.repo if origin.configured else repo
    used_branch = origin.branch if origin.configured else branch
    return (
        f"https://raw.githubusercontent.com/{owner}/{used_repo}/"
        f"{used_branch}/{path.lstrip('/')}"
    )


def http_referer() -> str:
    return resolve().http_referer


def openrouter_api_key() -> Optional[str]:
    return resolve().openrouter_api_key


def github_token() -> Optional[str]:
    return resolve().github_token


def has_openrouter_key() -> bool:
    return is_configured_secret(openrouter_api_key())


if __name__ == "__main__":
    import json

    origin = resolve()
    print(
        json.dumps(
            {
                "owner": origin.owner,
                "repo": origin.repo,
                "branch": origin.branch,
                "configured": origin.configured,
                "source": origin.source,
                "clone_url": origin.clone_url,
                "web_url": origin.web_url,
                "http_referer": origin.http_referer,
                "has_openrouter_key": bool(origin.openrouter_api_key),
                "has_github_token": bool(origin.github_token),
            },
            indent=2,
        )
    )
