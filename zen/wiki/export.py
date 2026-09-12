"""Export Visual Wiki resources for AI agent context."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .paths import VisualWikiPaths, visual_wiki_paths


def load_resources(paths: Optional[VisualWikiPaths] = None) -> List[Dict[str, Any]]:
    """Load curated resources from ``resources.json`` if present."""
    paths = paths or visual_wiki_paths()
    data_file = paths.resources_file
    if not data_file.is_file():
        return []
    try:
        payload = json.loads(data_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    return []


def build_agent_export(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build the same JSON shape as the web UI \"Export for AI\" action."""
    slim = [
        {
            "title": r.get("title", ""),
            "description": r.get("description", ""),
            "category": r.get("category", ""),
            "tags": r.get("tags", []),
            "link": r.get("link", ""),
        }
        for r in resources
    ]
    return {
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "total": len(slim),
        "resources": slim,
    }


def format_agent_prompt(resources: List[Dict[str, Any]]) -> str:
    """Format resources as a prompt-ready summary (matches the web UI)."""
    if not resources:
        return "Here is my curated visual wiki (0 resources):\n\n"
    lines = [
        f"• {r.get('title', 'Untitled')} — {r.get('description', '')} [{r.get('link', '')}]"
        for r in resources
    ]
    return (
        f"Here is my curated visual wiki ({len(resources)} resources):\n\n"
        + "\n".join(lines)
    )


def write_agent_context(
    output_dir: Optional[Path] = None,
    paths: Optional[VisualWikiPaths] = None,
) -> Dict[str, Path]:
    """Write JSON export and prompt text under ``~/.zenOS/context`` by default."""
    from .paths import default_agent_context_dir

    paths = paths or visual_wiki_paths()
    resources = load_resources(paths)
    export = build_agent_export(resources)
    prompt = format_agent_prompt(resources)

    out = output_dir or default_agent_context_dir()
    out.mkdir(parents=True, exist_ok=True)

    json_path = out / "visual-wiki.json"
    prompt_path = out / "visual-wiki-prompt.txt"
    json_path.write_text(json.dumps(export, indent=2), encoding="utf-8")
    prompt_path.write_text(prompt, encoding="utf-8")

    return {"json": json_path, "prompt": prompt_path}
