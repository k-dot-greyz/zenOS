"""env-doctor Harness Contract v1 — JSON payload and exit-code mapping."""

from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "1.0"
CHECK_FAMILIES = (
    "runtime",
    "package_manager",
    "lockfile",
    "secrets_presence",
    "git_state",
)

EXIT_HEALTHY = 0
EXIT_REPAIRABLE = 10
EXIT_BLOCKED = 20


def classify_report(report: Any) -> tuple[str, int]:
    """Map a DoctorReport to (status, semantic exit_code)."""
    checks = list(getattr(report, "checks", []) or [])
    if any(c.severity == "fail" and not getattr(c, "repairable", True) for c in checks):
        return "blocked", EXIT_BLOCKED
    if any(c.severity in {"fail", "warn"} for c in checks):
        return "repairable", EXIT_REPAIRABLE
    return "healthy", EXIT_HEALTHY


def process_exit_for_profile(exit_code: int, profile: str) -> int:
    """CI process exit is non-zero only for blocked (20). Semantic 10 stays in JSON."""
    if profile == "ci" and exit_code == EXIT_REPAIRABLE:
        return EXIT_HEALTHY
    return exit_code


def to_doctor_payload(report: Any, *, profile: str = "local") -> dict[str, Any]:
    """Serialize a DoctorReport into the portable env-doctor JSON contract."""
    status, code = classify_report(report)
    checks = []
    for check in getattr(report, "checks", []) or []:
        checks.append(
            {
                "id": check.name,
                "family": getattr(check, "family", "runtime"),
                "ok": bool(check.ok),
                "severity": check.severity,
                "repairable": bool(getattr(check, "repairable", True)),
                "message": check.message,
            }
        )
    doctor: dict[str, Any] = {
        "contract": CONTRACT_VERSION,
        "profile": profile,
        "status": status,
        "exit_code": code,
        "process_exit": process_exit_for_profile(code, profile),
        "checks": checks,
        "families": list(CHECK_FAMILIES),
        "outputs": {"human": "rich", "machine": "json"},
        "exit_codes": {
            str(EXIT_HEALTHY): "healthy",
            str(EXIT_REPAIRABLE): "repairable",
            str(EXIT_BLOCKED): "blocked",
        },
    }
    return {"doctor": doctor}
