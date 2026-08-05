"""Resolve Visual Wiki install locations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VISUAL_WIKI_REPO = "https://github.com/k-dot-greyz/visual-wiki.git"
DEFAULT_SUBMODULE_REL = Path("integrations") / "visual-wiki"


@dataclass(frozen=True)
class VisualWikiPaths:
    """Resolved paths for the Visual Wiki Next.js app."""

    root: Path
    resources_file: Path
    package_json: Path

    @property
    def is_checkout(self) -> bool:
        return self.package_json.is_file()


def resolve_visual_wiki_root(zenos_root: Optional[Path] = None) -> Path:
    """
    Resolve the Visual Wiki project root.

    Priority: ``ZEN_VISUAL_WIKI_PATH`` → ``~/.zenOS/visual-wiki`` →
    ``<zenos_root>/integrations/visual-wiki``.
    """
    env_path = os.environ.get("ZEN_VISUAL_WIKI_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()

    user_wiki = Path.home() / ".zenOS" / "visual-wiki"
    if user_wiki.is_dir() and (user_wiki / "package.json").is_file():
        return user_wiki.resolve()

    root = zenos_root or _find_zenos_root()
    return (root / DEFAULT_SUBMODULE_REL).resolve()


def visual_wiki_paths(zenos_root: Optional[Path] = None) -> VisualWikiPaths:
    """Return common paths for the resolved Visual Wiki root."""
    wiki_root = resolve_visual_wiki_root(zenos_root)
    return VisualWikiPaths(
        root=wiki_root,
        resources_file=wiki_root / "resources.json",
        package_json=wiki_root / "package.json",
    )


def _find_zenos_root() -> Path:
    """Walk parents from cwd to find a zenOS checkout."""
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "zen" / "cli.py").is_file():
            return candidate
    return cwd


def default_agent_context_dir() -> Path:
    return Path.home() / ".zenOS" / "context"
