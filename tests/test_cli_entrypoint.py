"""Console-script wiring: `zen` / `zenos` must resolve to zen.cli:main."""

from __future__ import annotations

from click.testing import CliRunner


def test_zen_group_help_via_main():
    from zen.cli import cli, main

    assert callable(main)
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "doctor" in result.output
    assert "env-doctor" in result.output


def test_receive_is_canonical_with_inbox_alias():
    from zen.cli import cli

    assert "receive" in cli.commands
    assert "inbox" in cli.commands
    assert cli.commands["receive"] is cli.commands["inbox"]
    runner = CliRunner()
    for name in ("receive", "inbox"):
        result = runner.invoke(cli, [name, "--help"])
        assert result.exit_code == 0, result.output
        assert "list" in result.output
        assert "add" in result.output
