"""PR #65 follow-up: zen receive UX + path traversal guards (ZEN65-REC-*)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner


def _seed_inbox(root: Path) -> None:
    for sub in ("incoming", "processing", "processed"):
        (root / "inbox" / sub).mkdir(parents=True, exist_ok=True)


def test_ZEN65_REC_01_happy_add_and_list_via_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Story: dev runs `zen receive add` then `list` and sees the new item."""
    monkeypatch.chdir(tmp_path)
    _seed_inbox(tmp_path)
    from zen.inbox import receive

    runner = CliRunner()
    add = runner.invoke(receive, ["add", "idea", "ship inbox tests"])
    assert add.exit_code == 0, add.output
    assert "Added idea item:" in add.output

    listed = runner.invoke(receive, ["list"])
    assert listed.exit_code == 0, listed.output
    assert "idea" in listed.output
    assert "ship inbox tests" in listed.output


def test_ZEN65_REC_02_sad_invalid_metadata_json_aborts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Story: malformed --metadata JSON must not create a partial inbox file."""
    monkeypatch.chdir(tmp_path)
    _seed_inbox(tmp_path)
    from zen.inbox import receive

    runner = CliRunner()
    result = runner.invoke(
        receive,
        ["add", "tool", "https://example.com", "--metadata", "{not-json"],
    )
    assert result.exit_code == 0
    assert "Invalid JSON metadata" in result.output
    assert list((tmp_path / "inbox" / "incoming").glob("*.json")) == []


def test_ZEN65_REC_03_happy_move_updates_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Story: move new → processing updates on-disk status."""
    monkeypatch.chdir(tmp_path)
    _seed_inbox(tmp_path)
    from zen.inbox import InboxManager, receive

    manager = InboxManager(str(tmp_path))
    item_id = manager.add_item("context", "agent handoff")
    runner = CliRunner()
    moved = runner.invoke(receive, ["move", item_id, "processing"])
    assert moved.exit_code == 0, moved.output
    assert "Moved" in moved.output

    data = json.loads((tmp_path / "inbox" / "processing" / f"{item_id}.json").read_text())
    assert data["status"] == "processing"


def test_ZEN65_REC_04_sad_move_unknown_item_graceful(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Story: moving a missing id prints a clear message (no traceback)."""
    monkeypatch.chdir(tmp_path)
    _seed_inbox(tmp_path)
    from zen.inbox import receive

    runner = CliRunner()
    result = runner.invoke(receive, ["move", "does-not-exist", "processed"])
    assert result.exit_code == 0
    assert "not found" in result.output.lower()


def test_ZEN65_REC_05_security_path_traversal_type_cannot_escape_incoming(tmp_path: Path):
    """Attack: item_type `../../../escape` must not write outside inbox/incoming."""
    from zen.inbox import InboxManager

    _seed_inbox(tmp_path)
    manager = InboxManager(str(tmp_path))
    evil = "../../../escape"
    item_id = manager.add_item(evil, "pwn")
    item_path = (tmp_path / "inbox" / "incoming" / f"{item_id}.json").resolve()
    assert item_path.is_file()
    assert str(item_path).startswith(str((tmp_path / "inbox" / "incoming").resolve()))
    assert not (tmp_path / "escape").exists()
    assert not (tmp_path.parent / "escape").exists()
    stored = json.loads(item_path.read_text())
    assert stored["type"] == evil


def test_ZEN65_REC_06_security_move_rejects_path_segments_in_item_id(tmp_path: Path):
    """Attack: move with `../` in item_id must not rename files outside inbox queues."""
    from zen.inbox import InboxManager

    _seed_inbox(tmp_path)
    manager = InboxManager(str(tmp_path))
    item_id = manager.add_item("note", "safe")
    assert manager.move_item(f"../{item_id}", "new", "processing") is False
    assert (tmp_path / "inbox" / "incoming" / f"{item_id}.json").is_file()
