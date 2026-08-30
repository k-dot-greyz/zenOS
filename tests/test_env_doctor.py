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


def test_startup_docs_require_python_3_14():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    quickstart = (ROOT / "docs" / "guides" / "QUICKSTART.md").read_text(encoding="utf-8")
    env_example = (ROOT / "env.example").read_text(encoding="utf-8")
    assert "Python 3.14" in readme
    assert "will not start" in readme
    assert "Python 3.14+" in quickstart
    assert "Python 3.14+" in env_example


def test_env_start_script_gates_python_3_14():
    start = (ROOT / "scripts" / "zenos-env-start.sh").read_text(encoding="utf-8")
    install = (ROOT / "scripts" / "zenos-env-install.sh").read_text(encoding="utf-8")
    assert "3.14" in start
    assert "require_runtime" in start
    assert "uv python install 3.14" in install


def test_pyproject_requires_python_3_14():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "Programming Language :: Python :: 3.8" not in pyproject
    assert "Programming Language :: Python :: 3.14" in pyproject
    from zen.setup.env_doctor import check_pyproject_python_floor

    result = check_pyproject_python_floor(root=ROOT)
    assert result.ok is True


def test_pyproject_floor_accepts_compound_spec(tmp_path: Path):
    from zen.setup.env_doctor import check_pyproject_python_floor

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nrequires-python = ">=3.14,<4"\n',
        encoding="utf-8",
    )
    result = check_pyproject_python_floor(root=tmp_path)
    assert result.ok is True


def test_pyproject_floor_rejects_3_12_bound(tmp_path: Path):
    from zen.setup.env_doctor import check_pyproject_python_floor

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nrequires-python = ">=3.12"\n',
        encoding="utf-8",
    )
    result = check_pyproject_python_floor(root=tmp_path)
    assert result.ok is False
    assert result.severity == "fail"


def test_min_python_is_the_runtime_constant():
    from zen.runtime import MIN_PYTHON as runtime_floor
    from zen.setup.env_doctor import MIN_PYTHON as doctor_floor
    from zen.setup.troubleshooter import MIN_PYTHON as trouble_floor

    assert runtime_floor is doctor_floor is trouble_floor
    assert runtime_floor == (3, 14)


def test_env_doctor_skips_outdated_by_default(monkeypatch):
    from zen.setup import env_doctor as ed

    called = {"n": 0}

    def boom(*_a, **_k):
        called["n"] += 1
        raise AssertionError("pip outdated must be opt-in")

    monkeypatch.setattr(ed, "check_outdated_packages", boom)
    report = ed.run_env_doctor(root=ROOT, include_outdated=False)
    assert called["n"] == 0
    assert report.checks


def test_fallback_requirements_match_runtime_imports():
    from zen.setup.unified_setup import FALLBACK_REQUIREMENTS

    required = (
        "click",
        "rich",
        "pyyaml",
        "jinja2",
        "pydantic",
        "aiohttp",
        "httpx",
        "python-dotenv",
        "prompt-toolkit",
        "beautifulsoup4",
        "schedule",
        "aiofiles",
        "psutil",
    )
    text = FALLBACK_REQUIREMENTS.lower()
    for name in required:
        assert name in text, name
    assert "nltk" not in text


def test_install_sh_windows_uses_python_bin_module_entrypoint():
    text = (ROOT / "install.sh").read_text(encoding="utf-8")
    assert "python zen/cli.py --help" not in text
    assert "$env:PYTHONPATH = \"$PWD\"" not in text.split("install_sample()")[1].split("main()")[0]
    assert '"$PYTHON_BIN" -m zen.cli --help' in text
    assert "Set-Alias -Name zenos -Value" in text
    assert "-m zen.cli" in text


def test_env_install_restores_setup_py_on_failure():
    install = (ROOT / "scripts" / "zenos-env-install.sh").read_text(encoding="utf-8")
    assert "trap" in install
    assert "_setup.py.bak" in install


def test_env_start_fails_without_zen_runtime():
    start = (ROOT / "scripts" / "zenos-env-start.sh").read_text(encoding="utf-8")
    assert "cannot import zen.runtime" in start
    assert "aiofiles" in start or "require_runtime()" in start


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
