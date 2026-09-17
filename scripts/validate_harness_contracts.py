#!/usr/bin/env python3
"""Validate Harness Contract v1 artifacts (pr-intent + dex registry).

Exit 0 when schemas and instances are healthy. Used by CI as the
registry-validation step (ZEN-313).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--changed",
        nargs="*",
        default=[],
        help="Changed paths (git diff). Used to enforce touches_contracts.",
    )
    parser.add_argument(
        "--others-json",
        type=Path,
        default=None,
        help="JSON list of {number, files} for open PRs used in overlap checks.",
    )
    args = parser.parse_args(argv)

    sys.path.insert(0, str(ROOT))
    from zen.contracts.pr_intent import (
        load_pr_intent,
        overlap_violations,
        validate_touches_contracts,
    )
    from zen.contracts.registry import load_registry

    intent_path = ROOT / ".github" / "pr-intent.yaml"
    registry_path = ROOT / "dex" / "registry.yaml"
    intent = load_pr_intent(intent_path)
    registry = load_registry(registry_path)
    if len(registry.entries) < 3:
        print(f"registry needs ≥3 entries, got {len(registry.entries)}", file=sys.stderr)
        return 20

    errors = []
    if args.changed:
        errors.extend(validate_touches_contracts(args.changed, declared=intent.touches_contracts))
    if args.others_json is not None:
        others_raw = json.loads(args.others_json.read_text(encoding="utf-8"))
        if not isinstance(others_raw, list):
            print("others-json must be a list of {number, files}", file=sys.stderr)
            return 20
        others = [(str(item["number"]), list(item.get("files") or [])) for item in others_raw]
        errors.extend(overlap_violations(args.changed, others, intent))
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 20

    print(
        f"pr-intent ok (intent={intent.intent} risk={intent.risk} "
        f"touches_contracts={intent.touches_contracts} expiry_days={intent.expiry_days})"
    )
    print(f"registry ok ({len(registry.entries)} entries, contract={registry.contract})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
