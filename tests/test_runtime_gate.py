"""Runtime floor: zenOS refuses to start below Python 3.14 or without core deps."""

from __future__ import annotations

import pytest

from zen.runtime import MIN_PYTHON, python_too_old, require_python, require_runtime


def test_runtime_floor_is_3_14():
    assert MIN_PYTHON == (3, 14)


def test_python_too_old_for_3_13():
    assert python_too_old((3, 13, 11)) is True
    assert python_too_old((3, 14, 0)) is False
    assert python_too_old((3, 14, 7)) is False


def test_require_python_exits_below_3_14():
    with pytest.raises(SystemExit) as exc:
        require_python(version_info=(3, 12, 3))
    assert exc.value.code == 1


def test_require_python_passes_on_3_14():
    require_python(version_info=(3, 14, 7))


def test_require_runtime_passes_on_this_interpreter():
    require_runtime()


def test_main_invokes_runtime_gate(monkeypatch):
    from zen import cli as zen_cli

    called: list[str] = []

    def fake_require() -> None:
        called.append("require")

    monkeypatch.setattr(zen_cli, "require_runtime", fake_require)
    monkeypatch.setattr(zen_cli, "cli", lambda: called.append("cli"))
    zen_cli.main()
    assert called == ["require", "cli"]
