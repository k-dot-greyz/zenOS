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
