#!/usr/bin/env python3
"""Fail if personal GitHub/user identity remains in the working tree.

zenOS is a template-friendly repo. Clone URLs, authors, CODEOWNERS, and
HTTP referers must not bake in a specific human or GitHub username.
Allowed placeholders: YOUR_GITHUB_USERNAME, YOUR_GITHUB_OWNER.
"""

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
    "scripts/check_no_identity_leaks.py",
    "tests/test_no_identity_leaks.py",
}

FORBIDDEN: Sequence[Tuple[str, Pattern[str]]] = (
    ("k-dot-greyz", re.compile(r"k-dot-greyz", re.IGNORECASE)),
    ("kasparsgreizis", re.compile(r"kasparsgreizis", re.IGNORECASE)),
    ("Kaspars Greizis", re.compile(r"Kaspars\s+Greizis", re.IGNORECASE)),
    ("kaspars.greizis", re.compile(r"kaspars\.greizis", re.IGNORECASE)),
    ("Kaspars", re.compile(r"\bKaspars\b")),
    ("kaspars", re.compile(r"\bkaspars\b", re.IGNORECASE)),
    ("k.greyZ", re.compile(r"\bk\.greyZ\b", re.IGNORECASE)),
    ("greyZ alias", re.compile(r"\bgreyZ\b")),
    ("personal vault path", re.compile(r"E:\\Vault\\Code")),
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
        print(f"FOUND {len(hits)} identity leak(s) under {root}:", file=sys.stderr)
        for hit in hits:
            print(f"  {hit}", file=sys.stderr)
        return 1
    print(f"OK: no personal identity tokens under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
