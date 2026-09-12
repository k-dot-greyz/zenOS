"""Centralized origin: one .env / git remote, no baked-in GitHub user."""

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
    is_configured_secret,
    parse_github_remote,
    resolve,
)

ROOT = Path(__file__).resolve().parents[1]


def _empty_env():
    return {
        "ZENOS_GITHUB_OWNER": "",
        "GITHUB_OWNER": "",
        "GITHUB_USERNAME": "",
        "ZENOS_REPO_NAME": "",
        "ZENOS_REPO_URL": "",
        "ZENOS_REPO_BRANCH": "",
        "ZENOS_HTTP_REFERER": "",
        "ZENOS_APP_URL": "",
        "ZENOS_PRIVATE_REPO": "",
        "OPENROUTER_API_KEY": "",
        "GITHUB_TOKEN": "",
    }


def test_parse_github_https_and_ssh():
    assert parse_github_remote("https://github.com/acme-org/zenOS.git") == (
        "acme-org",
        "zenOS",
    )
    assert parse_github_remote("https://github.com/acme-org/zenOS") == (
        "acme-org",
        "zenOS",
    )
    assert parse_github_remote("git@github.com:acme-org/zenOS.git") == (
        "acme-org",
        "zenOS",
    )
    assert parse_github_remote("ssh://git@github.com/acme-org/zenOS.git") == (
        "acme-org",
        "zenOS",
    )
    assert parse_github_remote(
        "https://x-access-token:sometoken@github.com/acme-org/zenOS.git"
    ) == ("acme-org", "zenOS")
    assert parse_github_remote("https://github.com/YOUR_GITHUB_USERNAME/zenOS.git") is None
    assert parse_github_remote("not-a-url") is None


def test_resolve_reads_dotenv_once(tmp_path: Path):
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "ZENOS_GITHUB_OWNER=acme-org",
                "ZENOS_REPO_NAME=zenOS",
                "OPENROUTER_API_KEY=sk-or-v1-from-dotenv",
                "GITHUB_TOKEN=ghp_from_dotenv",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    origin = resolve(root=tmp_path, environ=_empty_env(), git_remote=None)
    assert origin.configured is True
    assert origin.owner == "acme-org"
    assert origin.repo == "zenOS"
    assert origin.clone_url == "https://github.com/acme-org/zenOS.git"
    assert origin.openrouter_api_key == "sk-or-v1-from-dotenv"
    assert origin.github_token == "ghp_from_dotenv"
    assert origin.source == "dotenv"


def test_authenticated_remote_does_not_leak_token():
    origin = resolve(
        environ=_empty_env(),
        git_remote="https://x-access-token:sometoken@github.com/acme-org/zenOS.git",
        dotenv_path=None,
    )
    assert origin.configured is True
    assert origin.owner == "acme-org"
    assert origin.clone_url == "https://github.com/acme-org/zenOS.git"
    assert "x-access-token" not in origin.clone_url
    assert "sometoken" not in origin.clone_url


def test_resolve_uses_git_remote_when_env_empty():
    origin = resolve(
        environ=_empty_env(),
        git_remote="https://github.com/fork-user/zenOS.git",
        dotenv_path=None,
    )
    assert origin.configured is True
    assert origin.owner == "fork-user"
    assert origin.repo == "zenOS"
    assert origin.source == "git_remote"
    assert origin.clone_url == "https://github.com/fork-user/zenOS.git"


def test_explicit_env_wins_over_git_remote():
    env = _empty_env()
    env["ZENOS_GITHUB_OWNER"] = "from-env"
    origin = resolve(
        environ=env,
        git_remote="https://github.com/from-git/zenOS.git",
        dotenv_path=None,
    )
    assert origin.owner == "from-env"
    assert origin.source == "environ"


def test_repo_url_override_parses_owner():
    env = _empty_env()
    env["ZENOS_REPO_URL"] = "https://github.com/override-org/custom.git"
    origin = resolve(environ=env, git_remote=None, dotenv_path=None)
    assert origin.owner == "override-org"
    assert origin.repo == "custom"
    assert origin.clone_url == "https://github.com/override-org/custom.git"


def test_unconfigured_does_not_emit_fake_clone_url():
    origin = resolve(environ=_empty_env(), git_remote=None, dotenv_path=None)
    assert origin.configured is False
    assert origin.owner == PLACEHOLDER_OWNER
    assert origin.clone_url is None
    with pytest.raises(ValueError):
        origin.require_clone_url()


def test_github_owner_reads_zenos_env(monkeypatch):
    monkeypatch.delenv("GITHUB_USERNAME", raising=False)
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    monkeypatch.setenv("ZENOS_GITHUB_OWNER", "acme-org")
    assert github_owner() == "acme-org"


def test_github_owner_falls_back_to_placeholder(monkeypatch):
    monkeypatch.delenv("ZENOS_GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_USERNAME", raising=False)
    # Isolate from this checkout's real git remote
    monkeypatch.setattr("zen.origin.detect_git_remote", lambda root=None: None)
    assert github_owner() == PLACEHOLDER_OWNER


def test_repo_and_raw_urls_use_owner(monkeypatch):
    monkeypatch.setenv("ZENOS_GITHUB_OWNER", "acme-org")
    monkeypatch.delenv("ZENOS_REPO_URL", raising=False)
    assert github_repo_url() == "https://github.com/acme-org/zenOS.git"
    assert github_repo_url(git=False) == "https://github.com/acme-org/zenOS"
    assert (
        github_raw_url("install.sh")
        == "https://raw.githubusercontent.com/acme-org/zenOS/main/install.sh"
    )


def test_http_referer_defaults_to_product_site(monkeypatch):
    monkeypatch.delenv("ZENOS_HTTP_REFERER", raising=False)
    monkeypatch.delenv("ZENOS_APP_URL", raising=False)
    monkeypatch.setattr("zen.origin.detect_git_remote", lambda root=None: None)
    assert http_referer() == "https://zenos.ai"


def test_clone_all_repos_reads_origin(monkeypatch, tmp_path: Path):
    import clone_all_repos as cloner

    (tmp_path / ".env").write_text("ZENOS_GITHUB_OWNER=acme-org\n", encoding="utf-8")
    monkeypatch.delenv("GITHUB_USERNAME", raising=False)
    monkeypatch.delenv("ZENOS_GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    monkeypatch.chdir(tmp_path)
    args = SimpleNamespace(
        username=None,
        destination=tmp_path / "repos",
        dry_run=True,
        yes=True,
        include_private=False,
        exclude_forks=False,
        json=None,
    )
    config = cloner.get_configuration(args)
    assert config["usernames"] == ["acme-org"]


def test_clone_all_repos_requires_owner_when_nothing_configured(monkeypatch):
    import clone_all_repos as cloner

    monkeypatch.delenv("GITHUB_USERNAME", raising=False)
    monkeypatch.delenv("ZENOS_GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    monkeypatch.setattr("zen.origin.detect_git_remote", lambda root=None: None)
    monkeypatch.setattr("zen.origin._read_dotenv", lambda path: {})
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


def test_install_sh_loads_central_config():
    text = (ROOT / "install.sh").read_text(encoding="utf-8")
    assert "zenos-origin.sh" in text or "ZENOS_GITHUB_OWNER" in text
    assert "is_zenos_checkout" in text
    assert ".env" in text


def test_codeowners_is_commented_template():
    text = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "@YOUR_GITHUB_USERNAME" in text
    active = [
        line
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert active == []


def test_setup_commands_use_resolved_origin(monkeypatch):
    import get_setup_commands as setup

    monkeypatch.setenv("ZENOS_GITHUB_OWNER", "acme-org")
    monkeypatch.delenv("ZENOS_REPO_URL", raising=False)
    assert setup.repo_clone_url() == "https://github.com/acme-org/zenOS.git"


def test_setup_commands_use_git_remote_when_env_empty(monkeypatch):
    import get_setup_commands as setup

    for key in ("ZENOS_GITHUB_OWNER", "GITHUB_OWNER", "GITHUB_USERNAME", "ZENOS_REPO_URL"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(
        "zen.origin.detect_git_remote",
        lambda root=None: "https://github.com/fork-user/zenOS.git",
    )
    assert setup.repo_clone_url() == "https://github.com/fork-user/zenOS.git"


def test_openrouter_reads_key_from_origin(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-from-env")
    from zen.origin import openrouter_api_key

    assert openrouter_api_key() == "sk-or-v1-from-env"


def test_placeholder_and_empty_secrets_are_unset():
    assert is_configured_secret(None) is False
    assert is_configured_secret("") is False
    assert is_configured_secret("sk-or-v1-your-api-key-here") is False
    assert is_configured_secret("your-api-key-here") is False
    assert is_configured_secret("sk-or-v1-real-key") is True

    env = _empty_env()
    env["OPENROUTER_API_KEY"] = "sk-or-v1-your-api-key-here"
    env["GITHUB_TOKEN"] = "your_token_here"
    origin = resolve(environ=env, git_remote=None, dotenv_path=None)
    assert origin.openrouter_api_key is None
    assert origin.github_token is None


def test_empty_dotenv_key_does_not_count_as_configured(tmp_path: Path):
    (tmp_path / ".env").write_text("OPENROUTER_API_KEY=\nGITHUB_TOKEN=\n", encoding="utf-8")
    origin = resolve(root=tmp_path, environ=_empty_env(), git_remote=None)
    assert origin.openrouter_api_key is None
    assert origin.github_token is None


def test_start_scripts_use_origin_not_old_placeholder():
    start_sh = (ROOT / "start.sh").read_text(encoding="utf-8")
    start_ps1 = (ROOT / "start.ps1").read_text(encoding="utf-8")
    assert 'grep -q "sk-or-v1-your-api-key-here"' not in start_sh
    assert 'grep -q "sk-or-v1-your-api-key-here"' not in start_ps1
    assert "-match \"sk-or-v1-your-api-key-here\"" not in start_ps1
    assert "zenos-origin.sh" in start_sh
    assert "zenos_openrouter_key" in start_sh or "zenos_require_openrouter_key" in start_sh
    assert "Get-DotEnvValue" in start_ps1
    assert "OPENROUTER_API_KEY" in start_ps1


def test_termux_install_writes_openrouter_key_via_origin():
    text = (ROOT / "scripts" / "termux-install.sh").read_text(encoding="utf-8")
    assert "sk-or-v1-your-api-key-here" not in text
    assert "zenos_set_dotenv_value" in text
    assert "OPENROUTER_API_KEY" in text


def test_clone_all_repos_token_reads_origin(monkeypatch):
    import clone_all_repos as cloner

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr("zen.origin.github_token", lambda: "ghp_from_dotenv")

    class FakeResp:
        status_code = 200

        def json(self):
            return {"login": "acme-org"}

    monkeypatch.setattr(
        cloner,
        "requests",
        SimpleNamespace(get=lambda *a, **k: FakeResp(), RequestException=Exception),
    )
    assert cloner.get_github_token() == "ghp_from_dotenv"


def test_openrouter_provider_loads_key_from_dotenv(monkeypatch, tmp_path: Path):
    (tmp_path / ".env").write_text("OPENROUTER_API_KEY=sk-or-v1-from-dotenv\n", encoding="utf-8")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    from zen.providers.openrouter import OpenRouterProvider

    provider = OpenRouterProvider()
    assert provider.api_key == "sk-or-v1-from-dotenv"


def test_origin_sh_reads_dotenv(tmp_path: Path):
    script = ROOT / "scripts" / "zenos-origin.sh"
    (tmp_path / ".env").write_text("ZENOS_GITHUB_OWNER=acme-org\n", encoding="utf-8")
    import subprocess

    result = subprocess.run(
        ["bash", "-c", f"cd '{tmp_path}' && . '{script}' && zenos_github_owner && echo && zenos_github_clone_url"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert lines[0] == "acme-org"
    assert lines[1] == "https://github.com/acme-org/zenOS.git"


def test_origin_sh_openrouter_key_and_set_dotenv(tmp_path: Path):
    script = ROOT / "scripts" / "zenos-origin.sh"
    (tmp_path / ".env").write_text("OPENROUTER_API_KEY=\n", encoding="utf-8")
    import subprocess

    empty = subprocess.run(
        ["bash", "-c", f"cd '{tmp_path}' && . '{script}' && zenos_openrouter_key"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert empty.returncode != 0

    written = subprocess.run(
        [
            "bash",
            "-c",
            (
                f"cd '{tmp_path}' && . '{script}' && "
                "zenos_set_dotenv_value OPENROUTER_API_KEY sk-or-v1-set-once .env && "
                "zenos_openrouter_key"
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert written.returncode == 0, written.stderr
    assert written.stdout.strip() == "sk-or-v1-set-once"
    env_text = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "OPENROUTER_API_KEY=sk-or-v1-set-once" in env_text


def test_install_ps1_copies_env_example():
    text = (ROOT / "install.ps1").read_text(encoding="utf-8")
    assert "env.example" in text
    assert "OPENROUTER_API_KEY" in text


def test_env_example_is_the_ssot_for_identity_and_keys():
    text = (ROOT / "env.example").read_text(encoding="utf-8")
    for key in (
        "ZENOS_GITHUB_OWNER",
        "ZENOS_REPO_NAME",
        "ZENOS_REPO_URL",
        "OPENROUTER_API_KEY",
        "GITHUB_TOKEN",
    ):
        assert key in text
    # Keep values empty — never a personal GitHub username
    owner_line = next(
        line for line in text.splitlines() if line.startswith("ZENOS_GITHUB_OWNER=")
    )
    assert owner_line == "ZENOS_GITHUB_OWNER="
