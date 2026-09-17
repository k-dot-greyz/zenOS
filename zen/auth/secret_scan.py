"""Lightweight secret pattern scanner for pre-commit, CI, and the security lab.

Deliberately requires a full-looking token, not just the `ghp_` prefix, so
docs can mention token formats without tripping the hook.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

PATTERNS: tuple[tuple[str, str], ...] = (
    ("github_classic", r"ghp_[A-Za-z0-9]{20,}"),
    ("github_finegrained", r"github_pat_[A-Za-z0-9_]{20,}"),
    ("github_oauth", r"gho_[A-Za-z0-9]{20,}"),
    ("openrouter", r"sk-or-v1-[A-Za-z0-9]{20,}"),
    ("generic_sk", r"sk-[A-Za-z0-9]{20,}"),
    ("aws_access_key", r"AKIA[A-Z0-9]{16}"),
    ("bearer", r"Bearer [A-Za-z0-9._\-/=+]{20,}"),
)


@dataclass(frozen=True)
class SecretHit:
    kind: str
    match: str
    line: int


def _compile():
    import re

    return [(kind, re.compile(pattern)) for kind, pattern in PATTERNS]


_COMPILED = None


def scan_text(text: str) -> list[SecretHit]:
    global _COMPILED
    if _COMPILED is None:
        _COMPILED = _compile()
    hits: list[SecretHit] = []
    seen: set[tuple[str, int]] = set()
    for line_no, line in enumerate(text.splitlines(), start=1):
        for kind, regex in _COMPILED:
            found = regex.search(line)
            if not found:
                continue
            key = (kind, line_no)
            if key in seen:
                continue
            seen.add(key)
            hits.append(SecretHit(kind=kind, match=found.group(0), line=line_no))
    return hits


def scan_paths(paths: Iterable[Path]) -> dict[str, list[SecretHit]]:
    results: dict[str, list[SecretHit]] = {}
    for path in paths:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = scan_text(text)
        if hits:
            results[str(path)] = hits
    return results


def scan_diff(diff_text: str) -> list[SecretHit]:
    added = []
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    return scan_text("\n".join(added))


def _redact(match: str) -> str:
    if len(match) <= 8:
        return match[:2] + "…"
    return match[:4] + "…" + match[-4:]


def format_hits(hits: list[SecretHit], *, source: str = "") -> str:
    if not hits:
        return "No secret patterns found.\n"
    lines = ["Potential secrets detected:"]
    for hit in hits:
        prefix = f"{source}:" if source else ""
        lines.append(f"  {prefix}L{hit.line} {hit.kind} {_redact(hit.match)}")
    lines.append("Remove the secret, rotate it, and see docs/guides/SECRET_INCIDENT_RESPONSE.md")
    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="zenOS secret pattern scanner")
    parser.add_argument("--staged", action="store_true", help="Scan git diff --cached only")
    parser.add_argument("--root", default=".", help="Repo root for a full tree scan")
    args = parser.parse_args(argv)
    if args.staged:
        proc = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=False,
        )
        hits = scan_diff(proc.stdout or "")
        sys.stdout.write(format_hits(hits, source="staged"))
        return 1 if hits else 0
    root = Path(args.root)
    skip_parts = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache"}
    files = [
        p
        for p in root.rglob("*")
        if p.is_file() and not any(part in skip_parts for part in p.parts)
    ]
    grouped = scan_paths(files)
    exit_code = 0
    if not grouped:
        sys.stdout.write("No secret patterns found.\n")
        return 0
    for source, hits in grouped.items():
        sys.stdout.write(format_hits(hits, source=source))
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
