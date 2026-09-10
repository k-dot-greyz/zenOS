"""Harness Contract v1 — dex capability registry.

Guiding story: every dex entry answers four questions — what, how, proof,
supersedes — so `zen dex search` is machine-actionable instead of a
vibes-based YAML dump.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "dex" / "registry.yaml"
SCHEMA_PATH = ROOT / "contracts" / "harness-v1" / "capability-registry.schema.json"


@pytest.mark.contract
def test_registry_and_schema_exist():
    assert REGISTRY_PATH.is_file()
    assert SCHEMA_PATH.is_file()


@pytest.mark.contract
def test_registry_has_at_least_three_valid_entries():
    from zen.contracts.registry import load_registry

    registry = load_registry(REGISTRY_PATH)
    assert registry.contract == "1.0"
    assert len(registry.entries) >= 3
    ids = {entry.id for entry in registry.entries}
    assert "env-doctor" in ids
    for entry in registry.entries:
        assert entry.what.owner
        assert entry.what.maturity
        assert entry.what.risk
        assert entry.what.purpose
        assert entry.how.entrypoint
        assert entry.how.env_doctor_profile in {"ci", "local"}
        assert entry.proof.test
        assert entry.proof.artifact
        assert hasattr(entry, "supersedes")


@pytest.mark.contract
def test_invalid_entry_fails_validation():
    from zen.contracts.registry import RegistryError, validate_entry

    with pytest.raises(RegistryError):
        validate_entry(
            {
                "id": "broken",
                "what": {"owner": "x"},
                "how": {},
                "proof": {},
            }
        )


@pytest.mark.harness
def test_search_finds_env_doctor_by_purpose():
    from zen.contracts.registry import load_registry, search_registry

    registry = load_registry(REGISTRY_PATH)
    hits = search_registry(registry, "preflight")
    assert any(h.id == "env-doctor" for h in hits)
    empty = search_registry(registry, "definitely-not-a-capability-zzzz")
    assert empty == []


@pytest.mark.harness
def test_cli_dex_search_env_doctor():
    from zen.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["dex", "search", "env-doctor"])
    assert result.exit_code == 0, result.output
    assert "env-doctor" in result.output
    json_result = runner.invoke(cli, ["dex", "search", "env-doctor", "--format", "json"])
    assert json_result.exit_code == 0, json_result.output
    assert "env-doctor" in json_result.output
