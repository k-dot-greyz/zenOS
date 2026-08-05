#!/usr/bin/env python3
"""Simple tests for Visual Wiki integration."""

import json
import sys
from pathlib import Path

sys.path.insert(0, ".")


def test_imports():
    from zen.wiki import build_agent_export, load_resources, resolve_visual_wiki_root
    from zen.wiki.cli import wiki

    assert wiki is not None
    root = resolve_visual_wiki_root(Path.cwd())
    assert root.name == "visual-wiki"


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


def test_write_agent_context(tmp_path: Path):
    from zen.wiki.export import write_agent_context
    from zen.wiki.paths import VisualWikiPaths

    wiki_root = Path.cwd() / "integrations" / "visual-wiki"
    if not wiki_root.is_dir():
        return

    paths = VisualWikiPaths(
        root=wiki_root,
        resources_file=wiki_root / "resources.json",
        package_json=wiki_root / "package.json",
    )
    written = write_agent_context(output_dir=tmp_path, paths=paths)
    assert written["json"].is_file()
    payload = json.loads(written["json"].read_text())
    assert "resources" in payload


if __name__ == "__main__":
    test_imports()
    test_export_shape()
    print("OK: visual wiki tests passed")
