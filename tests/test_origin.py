"""Owner-agnostic origin helpers — no baked-in GitHub username."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from zen.origin import (
    PLACEHOLDER_OWNER,
    github_owner,
    github_raw_url,
    github_repo_url,
    http_referer,
)

ROOT = Path(__file__).resolve().parents[1]


def test_github_owner_reads_zenos_env(monkeypatch):
    monkeypatch.delenv("GITHUB_USERNAME", raising=False)
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    monkeypatch.setenv("ZENOS_GITHUB_OWNER", "acme-org")
    assert github_owner() == "acme-org"


def test_github_owner_falls_back_to_placeholder(monkeypatch):
    monkeypatch.delenv("ZENOS_GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_USERNAME", raising=False)
    assert github_owner() == PLACEHOLDER_OWNER


def test_repo_and_raw_urls_use_owner(monkeypatch):
    monkeypatch.setenv("ZENOS_GITHUB_OWNER", "acme-org")
    assert github_repo_url() == "https://github.com/acme-org/zenOS.git"
    assert github_repo_url(git=False) == "https://github.com/acme-org/zenOS"
    assert (
        github_raw_url("install.sh")
        == "https://raw.githubusercontent.com/acme-org/zenOS/main/install.sh"
    )


def test_http_referer_defaults_to_product_site(monkeypatch):
    monkeypatch.delenv("ZENOS_HTTP_REFERER", raising=False)
    monkeypatch.delenv("ZENOS_APP_URL", raising=False)
    assert http_referer() == "https://zenos.ai"


def test_clone_all_repos_requires_owner(monkeypatch):
    import clone_all_repos as cloner

    monkeypatch.delenv("GITHUB_USERNAME", raising=False)
    monkeypatch.delenv("ZENOS_GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    args = SimpleNamespace(
        username=None,
        destination=None,
        dry_run=True,
        yes=True,
        include_private=False,
        exclude_forks=False,
        json=None,
    )
    with pytest.raises(SystemExit) as exc:
        cloner.get_configuration(args)
    assert exc.value.code == 2


def test_install_sh_requires_owner_env():
    text = (ROOT / "install.sh").read_text(encoding="utf-8")
    assert "ZENOS_GITHUB_OWNER" in text
    assert "is_zenos_checkout" in text


def test_codeowners_is_commented_template():
    text = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "@YOUR_GITHUB_USERNAME" in text
    active = [
        line
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert active == []


def test_setup_commands_use_placeholder_or_env(monkeypatch):
    import get_setup_commands as setup

    monkeypatch.delenv("ZENOS_GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_USERNAME", raising=False)
    url = setup.repo_clone_url()
    assert url == "https://github.com/YOUR_GITHUB_USERNAME/zenOS.git"
    monkeypatch.setenv("ZENOS_GITHUB_OWNER", "acme-org")
    assert setup.repo_clone_url() == "https://github.com/acme-org/zenOS.git"
