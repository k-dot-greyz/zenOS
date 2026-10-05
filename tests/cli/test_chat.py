from __future__ import annotations


def test_chat_is_a_command(runner, zen_cli):
    result = runner.invoke(zen_cli, ["chat", "--help"])
    assert result.exit_code == 0
    assert "--offline" in result.output
    assert "--eco" in result.output


def test_run_chat_does_not_typeerror(runner, zen_cli, monkeypatch):
    monkeypatch.setattr("zen.cli._start_chat", lambda **kwargs: None)
    result = runner.invoke(zen_cli, ["run", "--chat"])
    assert result.exception is None
    assert result.exit_code == 0


def test_chat_non_tty_does_not_hang(runner, zen_cli):
    result = runner.invoke(zen_cli, ["chat"])
    assert result.exit_code == 1
    assert "TTY" in result.output or "tty" in result.output.lower()
