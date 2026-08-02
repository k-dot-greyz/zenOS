"""Branding gate: working tree must not contain Pokédex/Pokémon legacy tokens."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check_no_legacy_branding.py"


def test_no_legacy_branding_tokens():
    result = subprocess.run(
        [sys.executable, str(CHECK), "--root", str(ROOT)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        "Legacy branding tokens still present.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
