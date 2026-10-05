from __future__ import annotations

REQUIRED_COMMANDS = {
    "arena",
    "bench",
    "chat",
    "dex",
    "doctor",
    "env-doctor",
    "help",
    "inbox",
    "receive",
    "pkm",
    "plugins",
    "run",
    "setup",
    "sync",
}


def test_help_lists_required_commands(runner, zen_cli):
    result = runner.invoke(zen_cli, ["--help"])
    assert result.exit_code == 0
    for name in sorted(REQUIRED_COMMANDS):
        assert name in result.output, name


def test_no_args_prints_usage_exit_zero(runner, zen_cli):
    result = runner.invoke(zen_cli, [])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_version_flag_exit_zero(runner, zen_cli):
    from zen import __version__

    result = runner.invoke(zen_cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help_command_alias(runner, zen_cli):
    result = runner.invoke(zen_cli, ["help"])
    assert result.exit_code == 0
    assert "Commands:" in result.output
