"""Console-script wiring: `zen` / `zenos` must resolve to zen.cli:main."""

from __future__ import annotations

from click.testing import CliRunner


def test_zen_group_help_via_main():
    from zen.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "doctor" in result.output
    assert "env-doctor" in result.output
