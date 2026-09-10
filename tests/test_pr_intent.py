"""Harness Contract v1 — PR intake gate (`pr-intent`).

Guiding story: overlapping PRs stop silently rotting. Each PR declares
intent/risk/supersedes/depends_on/touches_contracts/expiry_days in
`.github/pr-intent.yaml`. Contract-touching diffs must flip the flag.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INTENT_PATH = ROOT / ".github" / "pr-intent.yaml"
SCHEMA_PATH = ROOT / "contracts" / "harness-v1" / "pr-intent.schema.json"

REQUIRED_FIELDS = (
    "intent",
    "risk",
    "supersedes",
    "depends_on",
    "touches_contracts",
    "expiry_days",
)


@pytest.mark.contract
def test_pr_intent_file_and_schema_exist():
    assert INTENT_PATH.is_file()
    assert SCHEMA_PATH.is_file()


@pytest.mark.contract
def test_repo_pr_intent_loads_and_has_required_fields():
    from zen.contracts.pr_intent import load_pr_intent

    intent = load_pr_intent(INTENT_PATH)
    for field in REQUIRED_FIELDS:
        assert hasattr(intent, field), field
    assert intent.intent
    assert intent.risk in {"low", "medium", "high"}
    assert isinstance(intent.supersedes, list)
    assert isinstance(intent.depends_on, list)
    assert isinstance(intent.touches_contracts, bool)
    assert intent.expiry_days >= 1
    # This PR lands the harness contracts themselves.
    assert intent.touches_contracts is True


@pytest.mark.contract
def test_overlapping_paths_require_supersedes():
    from zen.contracts.pr_intent import PrIntent, overlap_requires_supersedes

    bare = PrIntent(
        intent="feat",
        risk="low",
        supersedes=[],
        depends_on=[],
        touches_contracts=False,
        expiry_days=14,
    )
    declared = PrIntent(
        intent="feat",
        risk="medium",
        supersedes=["42"],
        depends_on=[],
        touches_contracts=True,
        expiry_days=14,
    )
    ours = ["zen/contracts/doctor.py", "README.md"]
    theirs = ["zen/contracts/doctor.py", "docs/guides/QUICKSTART.md"]
    assert overlap_requires_supersedes(ours, theirs, bare) is True
    assert overlap_requires_supersedes(ours, theirs, declared) is False
    assert overlap_requires_supersedes(ours, ["unrelated.py"], bare) is False


@pytest.mark.contract
def test_contract_paths_require_touches_contracts_flag():
    from zen.contracts.pr_intent import changed_paths_touch_contracts, validate_touches_contracts

    contract_paths = ["contracts/harness-v1/env-doctor.schema.json", "zen/cli.py"]
    docs_only = ["docs/guides/QUICKSTART.md"]
    assert changed_paths_touch_contracts(contract_paths) is True
    assert changed_paths_touch_contracts(docs_only) is False
    assert validate_touches_contracts(contract_paths, declared=True) == []
    errors = validate_touches_contracts(contract_paths, declared=False)
    assert errors
    assert validate_touches_contracts(docs_only, declared=False) == []


@pytest.mark.harness
def test_stale_when_age_exceeds_expiry_days():
    from zen.contracts.pr_intent import PrIntent, is_stale

    intent = PrIntent(
        intent="chore",
        risk="low",
        supersedes=[],
        depends_on=[],
        touches_contracts=False,
        expiry_days=14,
    )
    now = datetime(2026, 9, 10, tzinfo=timezone.utc)
    fresh = now - timedelta(days=3)
    expired = now - timedelta(days=15)
    assert is_stale(intent, created_at=fresh, now=now) is False
    assert is_stale(intent, created_at=expired, now=now) is True
