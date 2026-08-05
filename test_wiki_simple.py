#!/usr/bin/env python3
"""Simple tests for Visual Wiki integration."""

import json
import sys
from pathlib import Path

sys.path.insert(0, ".")


def test_imports():
    from zen.wiki import build_agent_export, locate_visual_wiki, resolve_visual_wiki_root
    from zen.wiki.cli import wiki

    assert wiki is not None
    root = resolve_visual_wiki_root(Path.cwd())
    assert root.name == "visual-wiki"
    _path, label = locate_visual_wiki(Path.cwd())
    assert isinstance(label, str)


def test_export_shape():
    from zen.wiki.export import build_agent_export, format_agent_prompt

    sample = [
        {
            "title": "Test",
            "description": "Desc",
            "category": "repo",
            "tags": ["a"],
            "link": "https://example.com",
        }
    ]
    export = build_agent_export(sample)
    assert export["total"] == 1
    assert export["resources"][0]["title"] == "Test"
    prompt = format_agent_prompt(sample)
    assert "visual wiki" in prompt
    assert "https://example.com" in prompt


def test_locate_dev_master_monkeypatch(monkeypatch=None):
    from zen.wiki import paths as wiki_paths

    fake_dm = Path("/tmp/fake-dev-master")
    wiki_path = fake_dm / "dex" / "09-repos" / "visual-wiki"
    try:
        wiki_path.mkdir(parents=True)
        (wiki_path / "package.json").write_text("{}", encoding="utf-8")
        original = wiki_paths.dev_master_root

        def _fake_root():
            return fake_dm

        wiki_paths.dev_master_root = _fake_root
        found, source = wiki_paths.locate_visual_wiki()
        assert found == wiki_path.resolve()
        assert "dev-master" in source
    finally:
        if "original" in dir():
            wiki_paths.dev_master_root = original
        shutil = __import__("shutil")
        if fake_dm.exists():
            shutil.rmtree(fake_dm, ignore_errors=True)


def test_write_agent_context(tmp_path: Path):
    from zen.wiki.export import write_agent_context
    from zen.wiki.paths import VisualWikiPaths

    wiki_root = tmp_path / "wiki"
    wiki_root.mkdir()
    (wiki_root / "package.json").write_text("{}", encoding="utf-8")
    (wiki_root / "resources.json").write_text("[]", encoding="utf-8")

    paths = VisualWikiPaths(
        root=wiki_root,
        resources_file=wiki_root / "resources.json",
        package_json=wiki_root / "package.json",
        source="test",
    )
    written = write_agent_context(output_dir=tmp_path / "out", paths=paths)
    assert written["json"].is_file()
    payload = json.loads(written["json"].read_text())
    assert "resources" in payload


if __name__ == "__main__":
    test_imports()
    test_export_shape()
    test_locate_dev_master_monkeypatch()
    print("OK: visual wiki tests passed")
