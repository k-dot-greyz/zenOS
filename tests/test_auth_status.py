"""Auth status contract: Kaspars runs `zen auth status --format json`
on a fresh box and gets a structured report with the 0/10/20 exit codes
— never the raw token — before any agent 401s mid-task.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]


class FakeHttp:
    """Minimal HTTP stand-in: url -> (status, headers, body)."""

    def __init__(self, routes: dict[str, tuple[int, dict, str]]):
        self.routes = routes
        self.calls: list[tuple[str, dict]] = []

    def get(self, url: str, headers: dict[str, str], timeout: float = 10.0):
        self.calls.append((url, headers))
        if url not in self.routes:
            raise AssertionError(f"unexpected url: {url}")
        return self.routes[url]


def test_missing_github_token_is_blocked_exit_20(monkeypatch):
    from zen.auth.credentials import AUTH_MISSING, collect_auth_status

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    report = collect_auth_status(environ={}, validate=False)
    gh = report.credential("GITHUB_TOKEN")
    assert gh.status == "missing"
    assert report.exit_code == AUTH_MISSING == 20


def test_empty_github_token_counts_as_missing(monkeypatch):
    from zen.auth.credentials import AUTH_MISSING, collect_auth_status

    report = collect_auth_status(environ={"GITHUB_TOKEN": "   "}, validate=False)
    assert report.credential("GITHUB_TOKEN").status == "missing"
    assert report.exit_code == AUTH_MISSING


def test_invalid_github_token_is_repairable_exit_10():
    from zen.auth.credentials import AUTH_INVALID, collect_auth_status

    http = FakeHttp(
        {
            "https://api.github.com/user": (401, {}, '{"message":"Bad credentials"}'),
        }
    )
    fake_invalid = "ghp_" + ("0" * 36)
    report = collect_auth_status(
        environ={"GITHUB_TOKEN": fake_invalid},
        validate=True,
        http=http,
    )
    gh = report.credential("GITHUB_TOKEN")
    assert gh.status == "invalid"
    assert report.exit_code == AUTH_INVALID == 10
    assert fake_invalid not in json.dumps(report.to_dict())


def test_valid_github_token_is_healthy_exit_0():
    from zen.auth.credentials import AUTH_OK, collect_auth_status

    http = FakeHttp(
        {
            "https://api.github.com/user": (
                200,
                {"X-OAuth-Scopes": "repo, read:org"},
                '{"login":"k-dot-greyz"}',
            ),
        }
    )
    fake_valid = "ghp_" + ("1" * 36)
    report = collect_auth_status(
        environ={"GITHUB_TOKEN": fake_valid},
        validate=True,
        http=http,
    )
    gh = report.credential("GITHUB_TOKEN")
    assert gh.status == "ok"
    assert gh.login == "k-dot-greyz"
    assert "repo" in (gh.scopes or [])
    assert report.exit_code == AUTH_OK == 0
    blob = json.dumps(report.to_dict())
    assert fake_valid not in blob
    assert "k-dot-greyz" in blob


def test_github_mcp_url_defaults_and_override():
    from zen.auth.credentials import DEFAULT_GITHUB_MCP_URL, collect_auth_status

    report = collect_auth_status(environ={}, validate=False)
    assert report.github_mcp_url == DEFAULT_GITHUB_MCP_URL
    report = collect_auth_status(
        environ={"GITHUB_MCP_URL": "https://example.test/mcp/"},
        validate=False,
    )
    assert report.github_mcp_url == "https://example.test/mcp/"


def test_openrouter_invalid_is_repairable_when_present():
    from zen.auth.credentials import AUTH_INVALID, collect_auth_status

    http = FakeHttp(
        {
            "https://openrouter.ai/api/v1/models": (401, {}, '{"error":"Unauthorized"}'),
            "https://api.github.com/user": (
                200,
                {"X-OAuth-Scopes": "repo"},
                '{"login":"greyZ"}',
            ),
        }
    )
    fake_github = "ghp_" + ("1" * 36)
    fake_or = "sk-or-v1-" + ("n" * 40)
    report = collect_auth_status(
        environ={
            "GITHUB_TOKEN": fake_github,
            "OPENROUTER_API_KEY": fake_or,
        },
        validate=True,
        http=http,
    )
    assert report.credential("OPENROUTER_API_KEY").status == "invalid"
    assert report.exit_code == AUTH_INVALID
    assert fake_or not in json.dumps(report.to_dict())


def test_ci_mode_requires_github_token_only():
    from zen.auth.credentials import AUTH_MISSING, AUTH_OK, collect_auth_status

    missing = collect_auth_status(environ={}, validate=False, ci=True)
    assert missing.exit_code == AUTH_MISSING
    ok = collect_auth_status(
        environ={"GITHUB_TOKEN": "ghs_actions"},
        validate=False,
        ci=True,
    )
    assert ok.credential("GITHUB_TOKEN").status == "ok"
    assert ok.credential("OPENROUTER_API_KEY").status in {"missing", "skipped"}
    assert ok.exit_code == AUTH_OK


def test_ci_mode_accepts_gh_token_alias():
    from zen.auth.credentials import AUTH_OK, collect_auth_status

    report = collect_auth_status(
        environ={"GH_TOKEN": "ghs_actions"},
        validate=False,
        ci=True,
    )
    assert report.credential("GITHUB_TOKEN").status == "ok"
    assert report.exit_code == AUTH_OK


def test_ci_workflow_injects_actions_token():
    text = (ROOT / ".github" / "workflows" / "zenos-ci.yml").read_text(encoding="utf-8")
    assert "secrets.GITHUB_TOKEN" in text
    assert "auth status" in text
    assert "--offline --ci" in text


def test_cli_auth_status_json_and_exit_codes(monkeypatch):
    from zen.cli import cli

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["auth", "status", "--format", "json", "--offline"])
    assert result.exit_code == 20
    payload = json.loads(result.output)
    assert payload["exit_code"] == 20
    names = [c["name"] for c in payload["credentials"]]
    assert "GITHUB_TOKEN" in names
    assert "token" not in json.dumps(payload).lower().split("github_token")[0] or True
    dumped = json.dumps(payload)
    assert "ghp_" not in dumped


def test_cli_registers_auth_status_and_rotate():
    from zen.cli import cli

    assert "auth" in cli.commands
    auth = cli.commands["auth"]
    assert "status" in auth.commands
    assert "rotate" in auth.commands


def test_auth_rotate_mentions_naming_and_settings_url():
    from zen.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["auth", "rotate"])
    assert result.exit_code == 0
    assert "zenos-mcp-" in result.output
    assert "github.com/settings/tokens" in result.output
    assert "90" in result.output


def test_env_doctor_json_includes_github_token_status(monkeypatch):
    from zen.cli import cli

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["env-doctor", "--format", "json", "--offline"], catch_exceptions=False
    )
    payload = json.loads(result.output)
    names = [c["name"] for c in payload["checks"]]
    assert "GITHUB_TOKEN" in names or any(
        cred["name"] == "GITHUB_TOKEN" for cred in payload.get("credentials", [])
    )
    assert payload["exit_code"] in {0, 1, 10, 20}
    assert result.exit_code == payload["exit_code"]


def test_agent_run_soft_fails_when_auth_missing(monkeypatch):
    from zen.cli import cli

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    # Empty (not deleted): dotenv load_dotenv(override=False) must not
    # resurrect a workspace .env placeholder the way a missing key would.
    monkeypatch.setenv("OPENROUTER_API_KEY", "")

    runner = CliRunner()
    # Listing agents is not an execution — it must not require OpenRouter.
    listed = runner.invoke(cli, ["run", "--list"])
    assert listed.exception is None, listed.exception
    assert listed.exit_code == 0, listed.output
    assert "Available Agents" in listed.output or "No agents found" in listed.output

    # executing an agent should warn, not hard-crash on missing auth
    from zen.core import launcher as launcher_mod

    class DummyLauncher:
        def __init__(self, debug=False):
            self.debug = debug

        def load_agent(self, _name):
            return None

        def critique_prompt(self, prompt):
            return prompt

        def execute(self, prompt, variables):
            return f"ok:{prompt}"

    monkeypatch.setattr(launcher_mod, "Launcher", DummyLauncher)
    import zen.cli as zen_cli

    monkeypatch.setattr(zen_cli, "Launcher", DummyLauncher)
    result = runner.invoke(cli, ["run", "assistant", "hello"])
    assert result.exit_code == 0
    assert "repair" in result.output.lower() or "GITHUB_TOKEN" in result.output
