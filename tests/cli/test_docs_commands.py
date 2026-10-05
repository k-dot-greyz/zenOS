from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_readme_does_not_advertise_zen_help_as_only_help():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "zen --help" in text or "zen help" in text


def test_startup_docs_use_run_list_not_top_level_list():
    for rel in (
        "README.md",
        "docs/guides/QUICKSTART.md",
        "docs/AI_INSTRUCTIONS.md",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "zen --list" not in text, rel
        assert "zen chat --copilot" not in text, rel
