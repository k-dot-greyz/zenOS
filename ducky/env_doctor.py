#!/usr/bin/env python3
"""
env-doctor — local environment diagnostics for ducky payloads.

Prefers zen.setup.env_doctor when the package is installed; otherwise uses a
stdlib-only collector so ducky works from USB before pip install.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DUCKY_ROOT = Path(__file__).resolve().parent
ZENOS_ROOT = DUCKY_ROOT.parent


def _command_available(name: str) -> bool:
    if shutil.which(name) is None:
        return False
    try:
        subprocess.run([name, "--version"], capture_output=True, timeout=5, check=False)
        return True
    except OSError, subprocess.TimeoutExpired:
        return False


def _detect_termux() -> bool:
    return bool(os.environ.get("TERMUX_VERSION")) or Path("/data/data/com.termux").is_dir()


def _detect_platform_name() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "darwin":
        return "macos"
    if system == "linux":
        return "termux" if _detect_termux() else "linux"
    return "unknown"


def _env_presence(zenos_root: Path) -> dict[str, Any]:
    env_path = zenos_root / ".env"
    example_path = zenos_root / "env.example"
    return {
        "env_file_exists": env_path.exists(),
        "env_example_exists": example_path.exists(),
        "openrouter_key_configured": bool(
            os.environ.get("OPENROUTER_API_KEY")
            and os.environ.get("OPENROUTER_API_KEY")
            not in ("", "your-api-key-here", "sk-or-v1-your-api-key-here")
        ),
    }


def _dex_status(zenos_root: Path) -> dict[str, bool]:
    dex = zenos_root / "dex"
    legacy = zenos_root / "pokedex"
    return {
        "models_yaml": (dex / "models.yaml").exists() or (legacy / "models.yaml").exists(),
        "procedures_yaml": (dex / "procedures.yaml").exists()
        or (legacy / "procedures.yaml").exists(),
        "arena_rankings_yaml": (dex / "arena_rankings.yaml").exists()
        or (legacy / "arena_rankings.yaml").exists(),
    }


def _hydration_source_hints(zenos_root: Path) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for label, raw in (
        ("ZEN_DEV_MASTER", os.environ.get("ZEN_DEV_MASTER", "")),
        ("../dev-master", str((zenos_root / "../dev-master").resolve())),
        ("../../dev-master", str((zenos_root / "../../dev-master").resolve())),
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


def _collect_standalone(zenos_root: Path) -> dict[str, Any]:
    py = sys.version_info
    python_version = f"{py.major}.{py.minor}.{py.micro}"
    issues: list[dict[str, Any]] = []
    passed = 0
    total = 3

    if py.major == 3 and py.minor >= 7:
        passed += 1
    else:
        issues.append({"message": f"Python {python_version} below 3.7", "fix_command": None})

    if _command_available("git"):
        passed += 1
    else:
        issues.append({"message": "git not available", "fix_command": "Install git"})

    if zenos_root.is_dir():
        passed += 1
    else:
        issues.append({"message": f"zenOS root missing: {zenos_root}", "fix_command": None})

    system = platform.system().lower()
    return {
        "schema": "zenos.ducky.local-deets/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "zenos_root": str(zenos_root),
        "ducky_root": str(DUCKY_ROOT),
        "collector": "standalone",
        "platform": {
            "name": _detect_platform_name(),
            "shell": Path(os.environ.get("SHELL", "unknown")).name,
            "python_version": python_version,
            "is_termux": _detect_termux(),
            "is_windows": system == "windows",
            "is_macos": system == "darwin",
            "is_linux": system == "linux",
            "git_available": _command_available("git"),
            "node_available": _command_available("node"),
            "user_home": str(Path.home()),
        },
        "env": _env_presence(zenos_root),
        "dex": _dex_status(zenos_root),
        "validation": {
            "passed": passed,
            "total": total,
            "issue_count": len(issues),
            "issues": issues,
        },
        "hydration_hints": _hydration_source_hints(zenos_root),
    }


def _collect_from_zen_doctor(zenos_root: Path) -> dict[str, Any]:
    if str(zenos_root) not in sys.path:
        sys.path.insert(0, str(zenos_root))

    from zen.setup.env_doctor import run_env_doctor  # noqa: PLC0415

    report = run_env_doctor(root=zenos_root)
    issues = [
        {
            "message": check.message,
            "fix_command": None,
            "severity": check.severity,
            "ok": check.ok,
        }
        for check in report.checks
        if not check.ok
    ]
    passed = sum(1 for check in report.checks if check.ok)
    total = len(report.checks)
    standalone = _collect_standalone(zenos_root)
    standalone["collector"] = "zen.setup.env_doctor"
    standalone["validation"] = {
        "passed": passed,
        "total": total,
        "issue_count": len(issues),
        "issues": issues,
    }
    standalone["zen_doctor_failures"] = report.has_failures
    return standalone


def collect_local_deets(zenos_root: Path | None = None) -> dict[str, Any]:
    root = (zenos_root or ZENOS_ROOT).resolve()
    try:
        return _collect_from_zen_doctor(root)
    except Exception:
        return _collect_standalone(root)


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
    platform_info = deets["platform"]
    print("\n🦆 ducky env-doctor\n")
    print(f"  Collector: {deets.get('collector', 'unknown')}")
    print(f"  Platform:  {platform_info['name']} ({platform_info['shell']})")
    print(f"  Python:    {platform_info['python_version']}")
    print(f"  Termux:    {'yes' if platform_info['is_termux'] else 'no'}")
    print(f"  Git:       {'yes' if platform_info['git_available'] else 'no'}")
    print(f"  Node:      {'yes' if platform_info['node_available'] else 'no'}")
    print(f"  .env:      {'found' if deets['env']['env_file_exists'] else 'missing'}")
    print(
        f"  API key:   {'configured' if deets['env']['openrouter_key_configured'] else 'not configured'}"
    )
    print(f"  Checks:    {deets['validation']['passed']}/{deets['validation']['total']} passed")
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
        default=None,
        help="Directory for JSON reports (default: <zenos-root>/.zen-hydration)",
    )
    parser.add_argument("--json-only", action="store_true", help="Suppress human summary")
    args = parser.parse_args()

    zenos_root = args.zenos_root.resolve()
    output_dir = args.output_dir or (zenos_root / ".zen-hydration")
    deets = collect_local_deets(zenos_root)
    local_path, report_path = write_reports(deets, output_dir)

    if not args.json_only:
        print_summary(deets)
        print(f"  Wrote: {local_path}")
        print(f"  Wrote: {report_path}")

    return 0 if deets["validation"]["issue_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
