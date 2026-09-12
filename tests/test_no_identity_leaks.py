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


def test_scanner_flags_forbidden_filename(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    leak = tmp_path / "docs" / "kaspars-notes.md"
    leak.write_text("neutral contents\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(CHECK), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr
    assert "kaspars-notes.md" in result.stderr
    assert "[path" in result.stderr


def test_scanner_flags_gemini_share_url(tmp_path: Path):
    (tmp_path / "note.md").write_text(
        "see https://g.co/gemini/share/deadbeef and " "https://gemini.google.com/gem/keep-this\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(CHECK), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr
    assert "g.co/gemini/share/" in result.stderr
    assert "gemini.google.com/gem/" not in result.stderr
