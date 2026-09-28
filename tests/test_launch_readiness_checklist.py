"""Launch readiness spec stays complete and discoverable."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs" / "planning" / "LAUNCH_READINESS_CHECKLIST.md"

INVARIANTS = (
    "Zero-egress static assets",
    "Affirmative clickwrap ledger",
    "Hardened age gate",
    "Default-deny telemetry and replay",
    "RFC 8058 outbound mail pipeline",
    "Symmetric click-to-cancel",
    "Pre-checkout renewal notice",
    "Merchant of Record (MoR) isolation",
    "DMCA safe harbor agent",
    "Accessibility navigation model",
    "Programmatic DSAR pipelines",
)

WIRED_FROM = (
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs" / "AI_INSTRUCTIONS.md",
    ROOT / "docs" / "archive" / "README.md",
    ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "launch_readiness.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
)


def test_checklist_file_exists():
    assert CHECKLIST.is_file(), "Launch readiness checklist is missing"


def test_checklist_defines_eleven_invariants():
    text = CHECKLIST.read_text(encoding="utf-8")
    missing = [item for item in INVARIANTS if item not in text]
    assert not missing, f"Checklist is missing invariants: {missing}"
    assert text.count("| [ ] |") >= 11, "Matrix is missing unchecked status cells"


def test_checklist_is_wired_from_contributor_paths():
    needle = "LAUNCH_READINESS_CHECKLIST.md"
    missing = []
    for path in WIRED_FROM:
        if needle not in path.read_text(encoding="utf-8"):
            missing.append(path.relative_to(ROOT).as_posix())
    assert not missing, f"Checklist is not linked from: {missing}"
