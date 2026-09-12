"""Identity gate: working tree must not bake in a specific GitHub user."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check_no_identity_leaks.py"


def test_no_personal_identity_tokens():
    result = subprocess.run(
        [sys.executable, str(CHECK), "--root", str(ROOT)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        "Personal GitHub/user identity still present.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
