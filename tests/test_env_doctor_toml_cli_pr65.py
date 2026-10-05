"""PR #65 follow-up: env-doctor TOML floor, report UX, CLI exit (ZEN65-DOC-*)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner


def test_ZEN65_DOC_01_sad_malformed_pyproject_toml(tmp_path: Path):
    """Story: corrupt pyproject.toml yields a readable [FAIL], not an uncaught decode error."""
    from zen.setup.env_doctor import check_pyproject_python_floor

    (tmp_path / "pyproject.toml").write_text("[project]\nrequires-python = '>=3.14'\nbroken", encoding="utf-8")
    result = check_pyproject_python_floor(root=tmp_path)
    assert result.ok is False
    assert result.severity == "fail"
    assert "unreadable" in result.message.lower()


def test_ZEN65_DOC_02_sad_missing_requires_python_field(tmp_path: Path):
    from zen.setup.env_doctor import check_pyproject_python_floor

    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
    result = check_pyproject_python_floor(root=tmp_path)
    assert result.ok is False
    assert "requires-python" in result.message


def test_ZEN65_DOC_03_happy_format_report_ok_and_warn_paths():
    from zen.setup.env_doctor import CheckResult, DoctorReport, format_report

    ok_report = DoctorReport(
        checks=[CheckResult("python", True, "ok", "Python 3.14 OK (floor 3.14)")]
    )
    assert "Result: OK" in format_report(ok_report)

    warn_report = DoctorReport(
        checks=[
            CheckResult("python", True, "ok", "ok"),
            CheckResult("dotenv", True, "warn", "copy env.example"),
        ]
    )
    assert "Result: WARN" in format_report(warn_report)

    fail_report = DoctorReport(
        checks=[CheckResult("python", False, "fail", "too old")]
    )
    assert "Result: FAIL" in format_report(fail_report)
    assert "zenOS env-doctor AI mode" in format_report(fail_report, ai_mode=True)


def test_ZEN65_DOC_04_cli_doctor_exits_1_when_report_has_failures(monkeypatch: pytest.MonkeyPatch):
    """Story: `zen doctor` must non-zero exit when env-doctor reports [FAIL] (CI gate)."""
    from zen.setup.env_doctor import CheckResult, DoctorReport

    def fake_run_env_doctor(**_kwargs):
        return DoctorReport(checks=[CheckResult("python", False, "fail", "nope")])

    monkeypatch.setattr("zen.setup.env_doctor.run_env_doctor", fake_run_env_doctor)
    from zen.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code == 1
    assert "FAIL" in result.output


def test_ZEN65_DOC_05_security_requires_python_fallback_regex_path(monkeypatch: pytest.MonkeyPatch):
    """Attack surface: odd requires-python strings when packaging.specifiers throws."""
    from zen.setup import env_doctor as ed

    def broken_spec(*_a, **_k):
        raise ValueError("simulated packaging failure")

    import packaging.specifiers as ps

    monkeypatch.setattr(ps, "SpecifierSet", broken_spec)
    assert ed.requires_python_meets_floor(">=3.14,<4") is True
    assert ed.requires_python_meets_floor(">=3.12") is False
    assert ed._requires_python_meets_floor_fallback("not-a-pep440-spec", ed.MIN_PYTHON) is False


def test_ZEN65_DOC_06_sad_outdated_scan_graceful_when_pip_missing(monkeypatch: pytest.MonkeyPatch):
    from zen.setup.env_doctor import check_outdated_packages

    def missing(*_a, **_k):
        raise FileNotFoundError("no pip")

    monkeypatch.setattr("subprocess.run", missing)
    result = check_outdated_packages(python_executable="python")
    assert result.severity == "warn"
    assert result.ok is True
    assert "Could not scan" in result.message


def test_ZEN65_DOC_07_happy_include_outdated_opt_in(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from zen.setup import env_doctor as ed

    monkeypatch.setattr(
        ed,
        "check_outdated_packages",
        lambda **_: ed.CheckResult("outdated", True, "ok", "skipped in test"),
    )
    report = ed.run_env_doctor(root=tmp_path, version_info=(3, 14, 0), include_outdated=True)
    names = [c.name for c in report.checks]
    assert "outdated" in names
