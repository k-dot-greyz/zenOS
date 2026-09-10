#!/usr/bin/env python3
"""Fail if Pokédex / Pokémon / Nintendo-adjacent branding remains in the tree."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, List, Pattern, Sequence, Tuple

ROOT_DEFAULT = Path(__file__).resolve().parents[1]

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    ".eggs",
    ".tox",
}

SKIP_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".so",
    ".o",
    ".a",
    ".bin",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp3",
    ".mp4",
    ".wav",
    ".zip",
    ".gz",
    ".xz",
    ".bz2",
}

# Self / tooling allowlist: these files intentionally mention forbidden tokens.
ALLOWLIST_RELATIVE = {
    "scripts/check_no_legacy_branding.py",
    "scripts/rebrand_to_dex.py",
    "tests/test_no_legacy_branding.py",
}

FORBIDDEN: Sequence[Tuple[str, Pattern[str]]] = (
    ("pokedex", re.compile(r"pok[eé]dex", re.IGNORECASE)),
    ("pokemon", re.compile(r"pok[eé]mon", re.IGNORECASE)),
    ("nintendo", re.compile(r"nintendo", re.IGNORECASE)),
    ("gotta catch", re.compile(r"gotta\s*catch", re.IGNORECASE)),
    ("BattleArena", re.compile(r"\bBattleArena\b")),
    ("get_pokedex", re.compile(r"\bget_pokedex\b")),
    ("sync_pokedex", re.compile(r"\bsync_pokedex\b")),
    ("Pokedex class", re.compile(r"\bPokedex\b")),
    ("pokedex_path", re.compile(r"\bpokedex_path\b")),
)


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        if any(part in SKIP_DIR_NAMES for part in rel_parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        yield path


def scan(root: Path) -> List[str]:
    hits: List[str] = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if rel in ALLOWLIST_RELATIVE:
            continue
        # After rebrand, the rebrand script itself may still be named with pokedex —
        # allowlist covers it. Also skip egg-info etc.
        if rel.endswith(".egg-info") or "/.egg-info/" in f"/{rel}/":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in FORBIDDEN:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                snippet = match.group(0)
                hits.append(f"{rel}:{line_no}: [{label}] {snippet}")
    return hits


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT_DEFAULT,
        help="Repository root to scan (default: repo root)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    hits = scan(root)
    if hits:
        print(f"FOUND {len(hits)} legacy branding hit(s) under {root}:", file=sys.stderr)
        for hit in hits:
            print(f"  {hit}", file=sys.stderr)
        return 1
    print(f"OK: no legacy branding tokens under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
