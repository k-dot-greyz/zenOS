#!/usr/bin/env python3
"""
env-doctor — local environment diagnostics for ducky payloads.

Wraps zenOS EnvironmentDetector + SetupTroubleshooter and emits machine-readable
local deets for hydration orchestration.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Resolve zenOS root (parent of ducky/)
DUCKY_ROOT = Path(__file__).resolve().parent
ZENOS_ROOT = DUCKY_ROOT.parent
SETUP_ROOT = ZENOS_ROOT / "zen" / "setup"
sys.path.insert(0, str(SETUP_ROOT))

# Import setup modules directly to avoid zen package __init__ side effects
from environment_detector import EnvironmentDetector  # noqa: E402
from troubleshooter import SetupTroubleshooter  # noqa: E402


def _env_presence() -> dict[str, Any]:
    env_path = ZENOS_ROOT / ".env"
    example_path = ZENOS_ROOT / "env.example"
    return {
        "env_file_exists": env_path.exists(),
        "env_example_exists": example_path.exists(),
        "openrouter_key_configured": bool(
            os.environ.get("OPENROUTER_API_KEY")
            and os.environ.get("OPENROUTER_API_KEY") not in ("", "your-api-key-here", "sk-or-v1-your-api-key-here")
        ),
    }


def _pokedex_status() -> dict[str, bool]:
    return {
        "models_yaml": (ZENOS_ROOT / "pokedex" / "models.yaml").exists(),
        "procedures_yaml": (ZENOS_ROOT / "pokedex" / "procedures.yaml").exists(),
        "arena_rankings_yaml": (ZENOS_ROOT / "pokedex" / "arena_rankings.yaml").exists(),
    }


def _hydration_source_hints() -> dict[str, Any]:
    candidates: list[dict[str, str]] = []
    for label, raw in (
        ("ZEN_DEV_MASTER", os.environ.get("ZEN_DEV_MASTER", "")),
        ("../dev-master", str((ZENOS_ROOT / "../dev-master").resolve())),
        ("../../dev-master", str((ZENOS_ROOT / "../../dev-master").resolve())),
    ):
        if not raw:
            continue
        path = Path(raw)
        candidates.append(
            {
                "label": label,
                "path": str(path),
                "exists": path.is_dir(),
                "has_hydration": (path / "hydration").is_dir() if path.is_dir() else False,
            }
        )
    return {"candidates": candidates}


def collect_local_deets(zenos_root: Path | None = None) -> dict[str, Any]:
    root = zenos_root or ZENOS_ROOT
    detector = EnvironmentDetector()
    env_info = detector.detect_environment(root)
    troubleshooter = SetupTroubleshooter()
    validation = troubleshooter.validate_system(env_info)

    issues = []
    for item in validation.get("issues", []):
        issues.append(
            {
                "message": getattr(item, "message", str(item)),
                "fix_command": getattr(item, "fix_command", None),
            }
        )

    return {
        "schema": "zenos.ducky.local-deets/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "zenos_root": str(root),
        "ducky_root": str(DUCKY_ROOT),
        "platform": {
            "name": env_info.platform,
            "shell": env_info.shell,
            "python_version": env_info.python_version,
            "is_termux": env_info.is_termux,
            "is_windows": env_info.is_windows,
            "is_macos": env_info.is_macos,
            "is_linux": env_info.is_linux,
            "git_available": env_info.git_available,
            "node_available": env_info.node_available,
            "user_home": str(env_info.user_home),
        },
        "env": _env_presence(),
        "pokedex": _pokedex_status(),
        "validation": {
            "passed": validation.get("validations_passed", 0),
            "total": validation.get("validations_total", 0),
            "issue_count": validation.get("total_issues", 0),
            "issues": issues,
        },
        "hydration_hints": _hydration_source_hints(),
    }


def write_reports(
    deets: dict[str, Any],
    output_dir: Path,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    local_path = output_dir / "local-deets.json"
    report_path = output_dir / "ducky-report.json"

    local_path.write_text(json.dumps(deets, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(deets, indent=2) + "\n", encoding="utf-8")
    return local_path, report_path


def print_summary(deets: dict[str, Any]) -> None:
    platform = deets["platform"]
    print("\n🦆 ducky env-doctor\n")
    print(f"  Platform:  {platform['name']} ({platform['shell']})")
    print(f"  Python:    {platform['python_version']}")
    print(f"  Termux:    {'yes' if platform['is_termux'] else 'no'}")
    print(f"  Git:       {'yes' if platform['git_available'] else 'no'}")
    print(f"  Node:      {'yes' if platform['node_available'] else 'no'}")
    print(f"  .env:      {'found' if deets['env']['env_file_exists'] else 'missing'}")
    print(
        f"  API key:   {'configured' if deets['env']['openrouter_key_configured'] else 'not configured'}"
    )
    print(
        f"  Checks:    {deets['validation']['passed']}/{deets['validation']['total']} passed"
    )
    if deets["validation"]["issue_count"]:
        print(f"  Issues:    {deets['validation']['issue_count']} need attention")
    print()


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="ducky env-doctor — local environment diagnostics")
    parser.add_argument(
        "--zenos-root",
        type=Path,
        default=ZENOS_ROOT,
        help="zenOS repository root (default: parent of ducky/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ZENOS_ROOT / ".zen-hydration",
        help="Directory for JSON reports",
    )
    parser.add_argument("--json-only", action="store_true", help="Suppress human summary")
    args = parser.parse_args()

    deets = collect_local_deets(args.zenos_root)
    local_path, report_path = write_reports(deets, args.output_dir)

    if not args.json_only:
        print_summary(deets)
        print(f"  Wrote: {local_path}")
        print(f"  Wrote: {report_path}")

    return 0 if deets["validation"]["issue_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
