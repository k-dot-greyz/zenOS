"""CLI help for the REST server entrypoints."""

import pytest

from zen.api.serve import build_parser, main
from zen.core import api as core_api


def test_serve_help_lists_host_and_port(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "--host" in out
    assert "--port" in out


def test_main_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "zenOS REST API" in capsys.readouterr().out


def test_core_api_shim_exports_main():
    assert core_api.main is main


def test_zen_serve_help():
    from click.testing import CliRunner

    from zen.cli import cli

    result = CliRunner().invoke(cli, ["serve", "--help"])
    assert result.exit_code == 0
    assert "--host" in result.output
    assert "--port" in result.output


def test_parse_bind_port_rejects_invalid_values():
    from zen.api.serve import parse_bind_port

    assert parse_bind_port(None) == 8080
    assert parse_bind_port("") == 8080
    assert parse_bind_port("9090") == 9090
    with pytest.raises(ValueError, match="Invalid API port"):
        parse_bind_port("nope")
    with pytest.raises(ValueError, match="Invalid API port"):
        parse_bind_port("70000")


def test_main_invalid_env_port_exits_2(monkeypatch):
    monkeypatch.setenv("ZEN_API_PORT", "not-a-port")
    assert main([]) == 2
