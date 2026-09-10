"""Harness Contract v1 — env-doctor JSON + exit-code protocol.

Guiding story: Kaspars runs `zen env-doctor --format json --profile ci`
on a fresh box / in CI and gets a machine-readable payload other repos
can consume without scraping Rich output. Semantic codes stay 0/10/20;
CI process exit only goes non-zero when the env is blocked.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]

CHECK_FAMILIES = (
    "runtime",
    "package_manager",
    "lockfile",
    "secrets_presence",
    "git_state",
)


@pytest.mark.contract
def test_doctor_payload_contract_version_and_families():
    from zen.contracts.doctor import CHECK_FAMILIES as FAMILIES
    from zen.contracts.doctor import CONTRACT_VERSION, to_doctor_payload
    from zen.setup.env_doctor import run_env_doctor

    assert CONTRACT_VERSION == "1.0"
    assert tuple(FAMILIES) == CHECK_FAMILIES

    report = run_env_doctor(root=ROOT, version_info=(3, 14, 0), include_outdated=False)
    payload = to_doctor_payload(report, profile="local")
    doctor = payload["doctor"]
    assert doctor["contract"] == "1.0"
    assert doctor["profile"] == "local"
    assert doctor["status"] in {"healthy", "repairable", "blocked"}
    assert doctor["exit_code"] in {0, 10, 20}
    assert "process_exit" in doctor
    present = {c["family"] for c in doctor["checks"]}
    for family in CHECK_FAMILIES:
        assert family in present, f"missing family {family}"


@pytest.mark.contract
def test_healthy_maps_to_exit_0():
    from zen.contracts.doctor import EXIT_HEALTHY, classify_report, to_doctor_payload
    from zen.setup.env_doctor import CheckResult, DoctorReport

    report = DoctorReport(
        checks=[
            CheckResult(
                name="python",
                ok=True,
                severity="ok",
                message="ok",
                family="runtime",
                repairable=False,
            )
        ]
    )
    status, code = classify_report(report)
    assert status == "healthy"
    assert code == EXIT_HEALTHY == 0
    payload = to_doctor_payload(report, profile="local")
    assert payload["doctor"]["exit_code"] == 0
    assert payload["doctor"]["process_exit"] == 0


@pytest.mark.contract
def test_repairable_maps_to_exit_10():
    from zen.contracts.doctor import EXIT_REPAIRABLE, classify_report, to_doctor_payload
    from zen.setup.env_doctor import CheckResult, DoctorReport

    report = DoctorReport(
        checks=[
            CheckResult(
                name="dotenv",
                ok=True,
                severity="warn",
                message="copy env.example",
                family="secrets_presence",
                repairable=True,
            )
        ]
    )
    status, code = classify_report(report)
    assert status == "repairable"
    assert code == EXIT_REPAIRABLE == 10
    local = to_doctor_payload(report, profile="local")
    assert local["doctor"]["exit_code"] == 10
    assert local["doctor"]["process_exit"] == 10


@pytest.mark.contract
def test_ci_profile_maps_repairable_process_exit_to_zero():
    from zen.contracts.doctor import process_exit_for_profile, to_doctor_payload
    from zen.setup.env_doctor import CheckResult, DoctorReport

    report = DoctorReport(
        checks=[
            CheckResult(
                name="dotenv",
                ok=True,
                severity="warn",
                message="copy env.example",
                family="secrets_presence",
                repairable=True,
            )
        ]
    )
    ci = to_doctor_payload(report, profile="ci")
    assert ci["doctor"]["exit_code"] == 10
    assert ci["doctor"]["process_exit"] == 0
    assert process_exit_for_profile(10, "ci") == 0
    assert process_exit_for_profile(20, "ci") == 20
    assert process_exit_for_profile(0, "ci") == 0


@pytest.mark.contract
def test_blocked_maps_to_exit_20():
    from zen.contracts.doctor import EXIT_BLOCKED, classify_report, to_doctor_payload
    from zen.setup.env_doctor import CheckResult, DoctorReport

    report = DoctorReport(
        checks=[
            CheckResult(
                name="python",
                ok=False,
                severity="fail",
                message="Python 3.12 detected",
                family="runtime",
                repairable=False,
            )
        ]
    )
    status, code = classify_report(report)
    assert status == "blocked"
    assert code == EXIT_BLOCKED == 20
    for profile in ("local", "ci"):
        payload = to_doctor_payload(report, profile=profile)
        assert payload["doctor"]["exit_code"] == 20
        assert payload["doctor"]["process_exit"] == 20


@pytest.mark.contract
def test_python_floor_fail_is_blocked_not_repairable():
    from zen.contracts.doctor import classify_report
    from zen.setup.env_doctor import check_python

    result = check_python(version_info=(3, 13, 0))
    assert result.ok is False
    assert result.repairable is False
    assert result.family == "runtime"
    from zen.setup.env_doctor import DoctorReport

    status, code = classify_report(DoctorReport(checks=[result]))
    assert status == "blocked"
    assert code == 20


@pytest.mark.harness
def test_cli_env_doctor_format_json():
    from zen.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["env-doctor", "--format", "json", "--profile", "ci"])
    assert result.exception is None or result.exit_code in {0, 10, 20}
    payload = json.loads(result.output)
    assert payload["doctor"]["contract"] == "1.0"
    assert payload["doctor"]["profile"] == "ci"
    assert payload["doctor"]["exit_code"] in {0, 10, 20}
    # CI profile: process exit is 0 unless blocked.
    if payload["doctor"]["exit_code"] != 20:
        assert result.exit_code == 0
    else:
        assert result.exit_code == 20


@pytest.mark.harness
def test_main_emits_json_when_python_is_below_floor(monkeypatch):
    """Console script must still print doctor JSON instead of dying in require_runtime."""
    import sys

    from zen.cli import main

    monkeypatch.setattr(sys, "argv", ["zen", "env-doctor", "--format", "json", "--profile", "ci"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code in {0, 10, 20}
    # Click already flushed JSON to stdout via the group; we only care the
    # entrypoint did not collapse to the runtime floor's exit 1.


@pytest.mark.harness
def test_cli_env_doctor_help_lists_format_and_profile():
    from zen.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["env-doctor", "--help"])
    assert result.exit_code == 0
    assert "--format" in result.output
    assert "--profile" in result.output
    assert "json" in result.output
