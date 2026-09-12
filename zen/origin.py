"""Owner-agnostic GitHub origin helpers.

Template checkouts must not bake in a specific human or GitHub username.
Set ZENOS_GITHUB_OWNER (or GITHUB_OWNER / GITHUB_USERNAME) after you fork.
"""

from __future__ import annotations

import os

REPO_NAME = "zenOS"
PLACEHOLDER_OWNER = "YOUR_GITHUB_USERNAME"
DEFAULT_HTTP_REFERER = "https://zenos.ai"
DEFAULT_BRANCH = "main"


def github_owner() -> str:
    """Return the GitHub user/org, or a template placeholder."""
    return (
        os.environ.get("ZENOS_GITHUB_OWNER")
        or os.environ.get("GITHUB_OWNER")
        or os.environ.get("GITHUB_USERNAME")
        or PLACEHOLDER_OWNER
    )


def github_repo_url(*, git: bool = True, repo: str = REPO_NAME) -> str:
    url = f"https://github.com/{github_owner()}/{repo}"
    return f"{url}.git" if git else url


def github_raw_url(path: str, *, branch: str = DEFAULT_BRANCH, repo: str = REPO_NAME) -> str:
    return (
        f"https://raw.githubusercontent.com/{github_owner()}/{repo}/"
        f"{branch}/{path.lstrip('/')}"
    )


def http_referer() -> str:
    """Product URL for OpenRouter HTTP-Referer — never a personal profile."""
    return (
        os.environ.get("ZENOS_HTTP_REFERER")
        or os.environ.get("ZENOS_APP_URL")
        or DEFAULT_HTTP_REFERER
    )
