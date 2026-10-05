from __future__ import annotations


def test_run_list_includes_builtin_agents(runner, zen_cli):
    result = runner.invoke(zen_cli, ["run", "--list"])
    assert result.exit_code == 0
    for name in ("troubleshooter", "critic", "assistant"):
        assert name in result.output


def test_run_unknown_agent_exits_one(runner, zen_cli, monkeypatch):
    class Boom(Exception):
        pass

    def fake_load(self, name):
        raise Boom(f"unknown agent {name}")

    monkeypatch.setattr("zen.core.launcher.Launcher.load_agent", fake_load)
    result = runner.invoke(zen_cli, ["run", "nope", "hi", "--no-critique"])
    assert result.exit_code == 1
    assert "failed" in result.output.lower() or "unknown" in result.output.lower()


def test_run_execute_uses_launcher(runner, zen_cli, monkeypatch):
    calls = {}

    class FakeLauncher:
        def __init__(self, debug=False):
            calls["debug"] = debug

        def load_agent(self, name):
            calls["agent"] = name

        def critique_prompt(self, prompt):
            return prompt

        def execute(self, prompt, variables):
            calls["prompt"] = prompt
            return "pong"

    monkeypatch.setattr("zen.cli.Launcher", FakeLauncher)
    result = runner.invoke(
        zen_cli, ["run", "assistant", "ping", "--no-critique"]
    )
    assert result.exit_code == 0
    assert calls["agent"] == "assistant"
    assert calls["prompt"] == "ping"
    assert "pong" in result.output
