"""Resolve Visual Wiki install locations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

VISUAL_WIKI_REPO = "https://github.com/k-dot-greyz/visual-wiki.git"
DEFAULT_USER_INSTALL = Path.home() / ".zenOS" / "visual-wiki"

# Canonical layout in dev-master (submodule target per visual-wiki EXTRACT docs).
DEV_MASTER_WIKI_CANDIDATES = (
    Path("dex") / "09-repos" / "visual-wiki",
    Path("projects") / "visual-wiki",
)

# Legacy zenOS path (removed from repo; still honored if present locally).
LEGACY_ZENOS_INTEGRATION = Path("integrations") / "visual-wiki"


@dataclass(frozen=True)
class VisualWikiPaths:
    """Resolved paths for the Visual Wiki Next.js app."""

    root: Path
    resources_file: Path
    package_json: Path
    source: str = "unknown"

    @property
    def is_checkout(self) -> bool:
        return self.package_json.is_file()


def dev_master_root() -> Optional[Path]:
    """Locate a dev-master superproject checkout."""
    env_path = os.environ.get("DEV_MASTER_ROOT")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.is_dir():
            return candidate.resolve()

    for candidate in (
        Path.home() / "Code" / "dev-master",
        Path.home() / "dev-master",
    ):
        if _looks_like_dev_master(candidate):
            return candidate.resolve()
    return None


def _looks_like_dev_master(path: Path) -> bool:
    return (path / "dex").is_dir() or (path / "AGENTS.md").is_file()


def _is_wiki_checkout(path: Path) -> bool:
    return (path / "package.json").is_file()


def locate_visual_wiki(zenos_root: Optional[Path] = None) -> Tuple[Optional[Path], str]:
    """
    Find an existing Visual Wiki checkout.

    Returns ``(path, source_label)`` or ``(None, reason)`` when nothing is installed.
    """
    env_path = os.environ.get("ZEN_VISUAL_WIKI_PATH")
    if env_path:
        root = Path(env_path).expanduser().resolve()
        if _is_wiki_checkout(root):
            return root, "ZEN_VISUAL_WIKI_PATH"
        return None, "ZEN_VISUAL_WIKI_PATH is set but not a Visual Wiki checkout"

    if _is_wiki_checkout(DEFAULT_USER_INSTALL):
        return DEFAULT_USER_INSTALL.resolve(), "~/.zenOS/visual-wiki"

    dm = dev_master_root()
    if dm:
        for rel in DEV_MASTER_WIKI_CANDIDATES:
            candidate = (dm / rel).resolve()
            if _is_wiki_checkout(candidate):
                return candidate, f"dev-master ({rel.as_posix()})"

    root = zenos_root or _find_zenos_root()
    legacy = (root / LEGACY_ZENOS_INTEGRATION).resolve()
    if _is_wiki_checkout(legacy):
        return legacy, "legacy integrations/visual-wiki (local only)"

    return None, "not installed"


def resolve_visual_wiki_root(zenos_root: Optional[Path] = None) -> Path:
    """
    Resolved Visual Wiki root for display and defaults.

    When no checkout exists, returns the recommended install path
    (``~/.zenOS/visual-wiki``).
    """
    found, _ = locate_visual_wiki(zenos_root)
    if found:
        return found
    return DEFAULT_USER_INSTALL.resolve()


def visual_wiki_paths(zenos_root: Optional[Path] = None) -> VisualWikiPaths:
    """Return common paths for the resolved Visual Wiki root."""
    found, source = locate_visual_wiki(zenos_root)
    wiki_root = found if found else DEFAULT_USER_INSTALL.resolve()
    return VisualWikiPaths(
        root=wiki_root,
        resources_file=wiki_root / "resources.json",
        package_json=wiki_root / "package.json",
        source=source,
    )


def dev_master_wiki_candidates() -> List[Path]:
    """Paths to check under dev-master (for status / docs)."""
    dm = dev_master_root()
    if not dm:
        return []
    return [(dm / rel).resolve() for rel in DEV_MASTER_WIKI_CANDIDATES]


def _find_zenos_root() -> Path:
    """Walk parents from cwd to find a zenOS checkout."""
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "zen" / "cli.py").is_file():
            return candidate
    return cwd


def default_agent_context_dir() -> Path:
    return Path.home() / ".zenOS" / "context"
