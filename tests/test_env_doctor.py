"""Env doctor + CLI entrypoint contracts.

Guiding story: Kaspars runs `zen env-doctor` on a fresh box and gets a
hard fail if Python is below 3.14, plus a real status dump of deps/CLI wiring.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_min_python_floor_is_3_14():
    from zen.setup.env_doctor import MIN_PYTHON

    assert MIN_PYTHON == (3, 14)


def test_check_python_rejects_anything_below_3_14():
    from zen.setup.env_doctor import check_python

    result = check_python(version_info=(3, 13, 11))
    assert result.ok is False
    assert result.severity == "fail"
    assert "3.14" in result.message


def test_check_python_accepts_3_14():
    from zen.setup.env_doctor import check_python

    result = check_python(version_info=(3, 14, 7))
    assert result.ok is True
    assert result.severity == "ok"


def test_cli_exposes_main_entrypoint():
    from zen.cli import main

    assert callable(main)


def test_cli_registers_doctor_and_env_doctor():
    from zen.cli import cli

    assert "doctor" in cli.commands
    assert "env-doctor" in cli.commands


def test_pyproject_requires_python_3_14():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.14"' in pyproject
    assert "Programming Language :: Python :: 3.8" not in pyproject
    assert "Programming Language :: Python :: 3.14" in pyproject


def test_ruff_uses_lint_select_not_deprecated_top_level_select():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.ruff.lint]" in pyproject
    # Top-level tool.ruff.select is deprecated in current Ruff.
    assert "\nselect = " not in pyproject.split("[tool.ruff]\n", 1)[-1].split("[", 1)[0]


def test_env_doctor_flags_root_setup_py_landmine(tmp_path: Path):
    from zen.setup.env_doctor import check_setup_py_landmine

    fake_root = tmp_path
    (fake_root / "setup.py").write_text("from zen.setup.unified_setup import main\n", encoding="utf-8")
    (fake_root / "pyproject.toml").write_text("[project]\nname='zenos'\n", encoding="utf-8")
    result = check_setup_py_landmine(root=fake_root)
    assert result.ok is False
    assert result.severity in {"fail", "warn"}
    assert "setup.py" in result.message.lower()


def test_troubleshooter_python_floor_is_3_14():
    from zen.setup.troubleshooter import MIN_PYTHON

    assert MIN_PYTHON == (3, 14)
