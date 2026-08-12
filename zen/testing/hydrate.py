"""
DECLARE → NEGOTIATE → HYDRATE provisioning for zenOS.

Implements the handshake from docs/testing-harness/PROVISIONING.md §3–§4.
Negotiation is pure and deterministic; HYDRATE is the only mutating phase.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore


class Phase(str, Enum):
    DECLARE = "declare"
    NEGOTIATE = "negotiate"
    HYDRATE = "hydrate"
    STATUS = "status"


class HydrateError(Exception):
    """Halt condition — no silent fallback."""


@dataclass
class Binding:
    requirement: str
    profile: str
    provider: str
    state: str
    provenance: List[str] = field(default_factory=list)
    note: Optional[str] = None


@dataclass
class Proposal:
    profile: str
    bindings: List[Binding]
    delta_add: List[str]
    delta_remove: List[str]
    delta_change: List[str]
    capability_requests: List[str]
    provenance: List[str]
    conformance_status: List[str]
    warnings: List[str]
    fingerprint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile,
            "bindings": [
                {
                    "requirement": b.requirement,
                    "profile": b.profile,
                    "provider": b.provider,
                    "state": b.state,
                    "provenance": b.provenance,
                    "note": b.note,
                }
                for b in self.bindings
            ],
            "deltaAdd": self.delta_add,
            "deltaRemove": self.delta_remove,
            "deltaChange": self.delta_change,
            "capabilityRequests": self.capability_requests,
            "provenance": self.provenance,
            "conformanceStatus": self.conformance_status,
            "warnings": self.warnings,
            "fingerprint": self.fingerprint,
        }


@dataclass
class HydrateJournal:
    path: Path

    def append(self, record: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")

    def read_all(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                lines.append(json.loads(line))
        return lines


def _root(root: Optional[Path] = None) -> Path:
    return root or Path.cwd()


def _load_toml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _profile_key(profile: str) -> str:
    return profile.replace("/", "_").replace("-", "_")


def _profile_section(policy: Dict[str, Any], profile: str) -> Dict[str, Any]:
    profiles = policy.get("profiles", {})
    key = _profile_key(profile)
    if key in profiles:
        return profiles[key]
    for section in profiles.values():
        if section.get("id") == profile:
            return section
    return {}


def _load_tokens(root: Path) -> Dict[str, Any]:
    return _load_toml(root / "tokens" / "testing-harness.toml")


def _load_policy(root: Path) -> Dict[str, Any]:
    return _load_toml(root / "policy" / "testing-harness.toml")


def _load_lock(root: Path) -> Dict[str, Any]:
    lock_path = root / "zenos.stack.lock"
    if not lock_path.exists():
        raise HydrateError(f"Missing binding lock: {lock_path}")
    return _load_toml(lock_path)


def _probe_environment(root: Path) -> Dict[str, Any]:
    """Read-only probes — DECLARE phase only."""

    def _run(cmd: List[str]) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=root,
            )
            return result.returncode == 0, (result.stdout or result.stderr).strip()
        except (subprocess.SubprocessError, OSError) as exc:
            return False, str(exc)

    py_ok, py_ver = _run([sys.executable, "--version"])
    pip_ok, pip_ver = _run([sys.executable, "-m", "pip", "--version"])
    git_ok, _ = _run(["git", "--version"])

    return {
        "python": {"ok": py_ok, "version": py_ver},
        "pip": {"ok": pip_ok, "version": pip_ver},
        "git": {"ok": git_ok},
        "platform": sys.platform,
        "root": str(root.resolve()),
    }


def declare(profile: str, root: Optional[Path] = None) -> Dict[str, Any]:
    """DECLARE — pure, offline, no mutation."""
    root = _root(root)
    policy = _load_policy(root)
    tokens = _load_tokens(root)
    lock = _load_lock(root)
    probes = _probe_environment(root)

    profile_section = _profile_section(policy, profile)
    if not profile_section:
        raise HydrateError(f"No policy profile for: {profile}")

    return {
        "phase": Phase.DECLARE.value,
        "profile": profile,
        "requirements": profile_section.get("requirements", []),
        "constraints": {
            "license": policy.get("license", {}),
            "network_granted": profile_section.get("network_granted", False),
            "native_toolchain_granted": profile_section.get(
                "native_toolchain_granted", False
            ),
        },
        "tokens": tokens,
        "lock_schema": lock.get("schema_version"),
        "probes": probes,
        "provenance": [
            "policy/testing-harness.toml",
            "tokens/testing-harness.toml",
            "zenos.stack.lock",
        ],
    }


def _bindings_for_profile(lock: Dict[str, Any], profile: str) -> List[Binding]:
    bindings: List[Binding] = []
    for entry in lock.get("bindings", []):
        if entry.get("profile") == profile:
            bindings.append(
                Binding(
                    requirement=entry["requirement"],
                    profile=entry["profile"],
                    provider=entry["provider"],
                    state=entry.get("state", "UNKNOWN"),
                    provenance=entry.get("provenance", []),
                    note=entry.get("note"),
                )
            )
    return bindings


def _fingerprint(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def negotiate(profile: str, root: Optional[Path] = None) -> Proposal:
    """NEGOTIATE — pure, offline, produces a deterministic proposal."""
    root = _root(root)
    declaration = declare(profile, root=root)
    lock = _load_lock(root)
    bindings = _bindings_for_profile(lock, profile)
    requirements = declaration["requirements"]
    warnings: List[str] = []
    conformance: List[str] = []

    bound_reqs = {b.requirement for b in bindings}
    missing = [r for r in requirements if r not in bound_reqs]
    if missing:
        raise HydrateError(
            f"No provider satisfies requirements under profile {profile}: {missing}"
        )

    for binding in bindings:
        if binding.state == "FAILED":
            raise HydrateError(
                f"Binding FAILED: {binding.requirement} → {binding.provider}"
            )
        if binding.state == "PROVISIONAL":
            warnings.append(
                f"PROVISIONAL: {binding.requirement} → {binding.provider}"
            )
        conformance.append(f"{binding.requirement}:{binding.state}")

    if not declaration["constraints"]["network_granted"]:
        warnings.append("Profile denies network — hydrate will not fetch packages")

    delta_add: List[str] = []
    providers = lock.get("providers", {})
    for binding in bindings:
        provider = providers.get(binding.provider, {})
        for pkg in provider.get("packages", []):
            delta_add.append(f"{pkg.get('name')}=={pkg.get('version')}")

    payload = {
        "profile": profile,
        "bindings": [b.requirement for b in bindings],
        "delta_add": sorted(delta_add),
        "requirements": sorted(requirements),
    }
    fp = _fingerprint(payload)

    return Proposal(
        profile=profile,
        bindings=bindings,
        delta_add=sorted(delta_add),
        delta_remove=[],
        delta_change=[],
        capability_requests=[],
        provenance=declaration["provenance"],
        conformance_status=conformance,
        warnings=warnings,
        fingerprint=fp,
    )


def observe(root: Optional[Path] = None) -> Dict[str, Any]:
    """P-observe — read actual state without mutation."""
    root = _root(root)
    probes = _probe_environment(root)
    journal = HydrateJournal(root / "ledger" / "hydrate.journal.jsonl")
    return {
        "probes": probes,
        "journal_entries": len(journal.read_all()),
        "requirements_lock_exists": (root / "requirements.txt").exists(),
    }


def status(profile: str = "ci/headless", root: Optional[Path] = None) -> Dict[str, Any]:
    """Combined observe + negotiate summary (no mutation)."""
    proposal = negotiate(profile, root=root)
    actual = observe(root=root)
    return {
        "profile": profile,
        "proposal_fingerprint": proposal.fingerprint,
        "warnings": proposal.warnings,
        "conformance": proposal.conformance_status,
        "actual": actual,
    }


def hydrate(
    profile: str,
    root: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """HYDRATE — journaled plan/apply. Only mutating phase."""
    root = _root(root)
    proposal = negotiate(profile, root=root)
    journal_path = root / "ledger" / "hydrate.journal.jsonl"
    journal = HydrateJournal(journal_path)

    if not proposal.delta_add and profile == "ci/headless":
        # Still ensure requirements.txt install for zenOS core
        req = root / "requirements.txt"
        if req.exists():
            proposal.delta_add.append("requirements.txt")

    plan = {
        "profile": profile,
        "fingerprint": proposal.fingerprint,
        "steps": [],
    }

    if profile == "ci/headless":
        req_file = root / "requirements.txt"
        if req_file.exists():
            plan["steps"].append(
                {
                    "id": "pip-requirements",
                    "precondition": "requirements.txt exists",
                    "command": [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(req_file),
                    ],
                }
            )

    results: List[Dict[str, Any]] = []
    for step in plan["steps"]:
        record = {
            "at": datetime.now(timezone.utc).isoformat(),
            "phase": "hydrate",
            "step": step["id"],
            "status": "pending",
            "fingerprint": proposal.fingerprint,
        }
        journal.append({**record, "status": "started"})

        if dry_run:
            results.append({**step, "status": "dry_run"})
            journal.append({**record, "status": "dry_run"})
            continue

        cmd = step["command"]
        try:
            proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
            if proc.returncode != 0:
                journal.append(
                    {**record, "status": "failed", "stderr": proc.stderr[-500:]}
                )
                raise HydrateError(f"Hydrate step {step['id']} failed: {proc.stderr}")
            journal.append({**record, "status": "completed"})
            results.append({**step, "status": "completed"})
        except subprocess.SubprocessError as exc:
            journal.append({**record, "status": "failed", "error": str(exc)})
            raise HydrateError(f"Hydrate step {step['id']} error: {exc}") from exc

    return {
        "profile": profile,
        "fingerprint": proposal.fingerprint,
        "warnings": proposal.warnings,
        "steps": results,
        "dry_run": dry_run,
    }


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="zenOS harness hydrate handshake")
    parser.add_argument(
        "phase",
        choices=[p.value for p in Phase],
        help="DECLARE | NEGOTIATE | HYDRATE | STATUS",
    )
    parser.add_argument("--profile", default="ci/headless")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")

    args = parser.parse_args(argv)

    try:
        if args.phase == Phase.DECLARE.value:
            out = declare(args.profile, root=args.root)
        elif args.phase == Phase.NEGOTIATE.value:
            out = negotiate(args.profile, root=args.root).to_dict()
        elif args.phase == Phase.STATUS.value:
            out = status(args.profile, root=args.root)
        else:
            out = hydrate(args.profile, root=args.root, dry_run=args.dry_run)
    except HydrateError as exc:
        print(f"HALT: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(json.dumps(out, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
