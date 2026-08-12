"""Tests for zenOS testing harness hydrate handshake (PROVISIONING §4 properties)."""

import json
from pathlib import Path

import pytest

from zen.testing.hydrate import (
    HydrateError,
    declare,
    hydrate,
    negotiate,
    status,
)


ROOT = Path(__file__).resolve().parents[1]


def test_declare_ci_profile():
    decl = declare("ci/headless", root=ROOT)
    assert decl["profile"] == "ci/headless"
    assert "execute_test_plan" in decl["requirements"]
    assert decl["probes"]["python"]["ok"]


def test_negotiation_is_deterministic():
    p1 = negotiate("ci/headless", root=ROOT)
    p2 = negotiate("ci/headless", root=ROOT)
    assert p1.fingerprint == p2.fingerprint
    assert p1.to_dict() == p2.to_dict()


def test_negotiation_pure_function_byte_identical():
  """Same inputs → byte-identical proposal JSON (PROVISIONING §3)."""
  payloads = []
  for _ in range(3):
      p = negotiate("ci/headless", root=ROOT)
      payloads.append(json.dumps(p.to_dict(), sort_keys=True, separators=(",", ":")))
  assert payloads[0] == payloads[1] == payloads[2]


def test_failed_binding_halts():
    with pytest.raises(HydrateError, match="FAILED"):
        negotiate("linux/wayland/chromium/dev", root=ROOT)


def test_status_no_mutation():
    before = status("ci/headless", root=ROOT)
    after = status("ci/headless", root=ROOT)
    assert before == after


def test_hydrate_dry_run_is_noop_install():
    result = hydrate("ci/headless", root=ROOT, dry_run=True)
    assert result["dry_run"] is True
    assert all(s.get("status") == "dry_run" for s in result["steps"])


def test_tokens_perf_specimen_count_from_file():
    decl = declare("ci/headless", root=ROOT)
    assert decl["tokens"]["testing"]["perf_specimen_count"] == 120
