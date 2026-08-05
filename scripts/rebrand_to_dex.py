#!/usr/bin/env python3
"""
Programmatic Pokédex → Dex rebrand for zenOS.

Dry-run by default. Pass --apply to mutate the tree.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

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
}

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".sh",
    ".ps1",
    ".json",
    ".cfg",
    ".ini",
    ".example",
    ".code-workspace",
}

# Most-specific / longest first.
REPLACEMENTS: Sequence[Tuple[str, str]] = (
    ("Pokédex Control Center", "Dex"),
    ("PCC (Pokédex Control Center)", "Dex"),
    ("Model & Procedure Pokédex", "Model & Procedure Dex"),
    ("Procedure Pokédex", "Procedure Dex"),
    ("Model Pokédex", "Model Dex"),
    ("Plugin Pokédex", "Plugin Dex"),
    ("Pokédex of Plugins", "Dex of Plugins"),
    ("zenOS Pokédex", "zenOS Dex"),
    ("the Pokédex", "the Dex"),
    ("The Pokédex", "The Dex"),
    ("Explore the Pokédex", "Explore the Dex"),
    ("Accessing the Pokédex", "Accessing the Dex"),
    ("Pokédex Statistics", "Dex Statistics"),
    ("Pokédex Commands", "Dex Commands"),
    ("Pokédex Concept", "Dex Concept"),
    ("Pokédex Parallel", "Dex Parallel"),
    ("Pokédex Concepts", "Dex Concepts"),
    ("Pokédex system", "Dex system"),
    ("Basic Pokédex", "Basic Dex"),
    ("ModelCombatStats", "ModelBenchStats"),
    ("combat_stats", "bench_stats"),
    ("Battle Arena", "Model Bench"),
    ("BATTLE ARENA", "MODEL BENCH"),
    ("battle arena", "model bench"),
    ("BattleArena", "ModelBench"),
    ("battle_arena", "bench"),
    ("get_pokedex", "get_dex_catalog"),
    ("sync_pokedex", "sync_dex"),
    ("pokedex_path", "dex_path"),
    ("pokedex_instance", "dex_catalog_instance"),
    ("_pokedex_instance", "_dex_catalog_instance"),
    ("arena_rankings", "bench_rankings"),
    ("trainer_profile", "operator_profile"),
    ("class Pokedex", "class DexCatalog"),
    ("Pokedex(", "DexCatalog("),
    ("Pokedex)", "DexCatalog)"),
    ("Pokedex:", "DexCatalog:"),
    ("Pokedex ", "DexCatalog "),
    ("Pokedex\n", "DexCatalog\n"),
    ("from zen.pokedex", "from zen.dex"),
    ("import zen.pokedex", "import zen.dex"),
    ("zen.pokedex.", "zen.dex."),
    ("zen pokedex", "zen dex"),
    ("`pokedex/", "`dex/"),
    ("'pokedex/", "'dex/"),
    ('"pokedex/', '"dex/'),
    ('Path("pokedex")', 'Path("dex")'),
    ("Path('pokedex')", "Path('dex')"),
    ("pokedex/models.yaml", "dex/models.yaml"),
    ("pokedex/procedures.yaml", "dex/procedures.yaml"),
    ("pokedex/arena_rankings.yaml", "dex/bench_rankings.yaml"),
    ("pokedex.db", "dex.db"),
    ("/pokedex/", "/dex/"),
    ("Pokédex", "Dex"),
    ("pokédex", "dex"),
    ("POKEDEX", "DEX"),
    ("Pokedex", "DexCatalog"),
    ("pokedex", "dex"),
)

YAML_FIELD_REPLACEMENTS: Sequence[Tuple[str, str]] = (
    (r"^(\s*)abilities:", r"\1capabilities:"),
    (r"^(\s*)rarity:", r"\1tier:"),
)

CODE_FIELD_REPLACEMENTS: Sequence[Tuple[str, str]] = (
    (r"\bRarity\b", "Tier"),
    (r"get_models_by_rarity", "get_models_by_tier"),
    (r"model_rarities", "model_tiers"),
    (r"rarity_counts", "tier_counts"),
    (r"rarity_emoji", "tier_emoji"),
    (r"\.rarity\b", ".tier"),
    (r"\brarity=", "tier="),
    (r'\["rarity"\]', '["tier"]'),
    (r"\['rarity'\]", "['tier']"),
    (r'\.get\([\'"]rarity[\'"]', '.get("tier"'),
    (r'\.get\([\'"]abilities[\'"]', '.get("capabilities"'),
    (r"\babilities=", "capabilities="),
    (r'\["abilities"\]', '["capabilities"]'),
    (r"abilities=model", "capabilities=model"),
    (r"self\.abilities", "self.capabilities"),
)


def iter_text_files(root: Path) -> Iterable[Path]:
    """
    Recursively yield eligible text files under a repository root.
    
    Parameters:
        root (Path): Root directory to search.
    
    Yields:
        Path: Files with recognized text extensions or standard extensionless text filenames, excluding skipped directories.
    """
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(p in SKIP_DIR_NAMES for p in rel_parts):
            continue
        # Always process extensionless known scripts? only known suffixes + no suffix markdown-ish
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "Dockerfile",
            "Makefile",
            "LICENSE",
            "CODEOWNERS",
        }:
            continue
        # Don't rewrite this script's filename references incorrectly mid-flight —
        # still rewrite content except we want the script itself to keep "pokedex" in docs.
        yield path


def replace_text(content: str) -> Tuple[str, int]:
    """
    Apply the configured literal branding and identifier replacements to text content.
    
    Parameters:
    	content (str): The text to transform.
    
    Returns:
    	Tuple[str, int]: The transformed text and the number of replacements performed.
    """
    count = 0
    for old, new in REPLACEMENTS:
        if old in content:
            n = content.count(old)
            content = content.replace(old, new)
            count += n
    return content, count


def replace_yaml_fields(content: str) -> Tuple[str, int]:
    """
    Rename supported YAML field names in content.
    
    Parameters:
        content (str): YAML text to transform.
    
    Returns:
        Tuple[str, int]: The transformed YAML text and the number of replacements made.
    """
    count = 0
    lines = content.splitlines(keepends=True)
    out: List[str] = []
    for line in lines:
        original = line
        for pattern, repl in YAML_FIELD_REPLACEMENTS:
            line, n = re.subn(pattern, repl, line)
            count += n
        # also rewrite inline rarity: in comments already handled by REPLACEMENTS partially
        out.append(line)
        if line != original and count == 0:
            pass
    return "".join(out), count


def replace_code_fields(content: str) -> Tuple[str, int]:
    """
    Rename code-level field and identifier references related to tiers and capabilities.
    
    Parameters:
    	content (str): Source code to transform.
    
    Returns:
    	Tuple[str, int]: The transformed content and the number of replacements made.
    """
    count = 0
    for pattern, repl in CODE_FIELD_REPLACEMENTS:
        content, n = re.subn(pattern, repl, content)
        count += n
    return content, count


def write_or_report(path: Path, new_text: str, apply: bool) -> None:
    """Write transformed text to a file when apply mode is enabled."""
    if apply:
        path.write_text(new_text, encoding="utf-8")


def ensure_dex_package(root: Path, apply: bool, log: List[str]) -> None:
    """
    Ensure the repository's Dex package structure is present and migrate legacy Pokédex modules and data into it.
    
    Parameters:
        root (Path): Repository root containing the legacy and destination paths.
        apply (bool): Whether to perform filesystem changes instead of only recording planned operations.
        log (List[str]): List to which planned or applied operations are appended.
    """
    dex_pkg = root / "zen" / "dex"
    init = dex_pkg / "__init__.py"
    if apply:
        dex_pkg.mkdir(parents=True, exist_ok=True)
    log.append(f"{'APPLY' if apply else 'PLAN'}: ensure {dex_pkg}/")

    # Move zen/pokedex.py → zen/dex/catalog.py
    old_mod = root / "zen" / "pokedex.py"
    catalog = dex_pkg / "catalog.py"
    if old_mod.exists():
        log.append(
            f"{'APPLY' if apply else 'PLAN'}: move {old_mod.relative_to(root)} -> {catalog.relative_to(root)}"
        )
        if apply:
            if catalog.exists():
                catalog.unlink()
            shutil.move(str(old_mod), str(catalog))

    # Move package files
    old_pkg = root / "zen" / "pokedex"
    mapping = {
        "battle_arena.py": "bench.py",
        "openrouter_sync.py": "openrouter_sync.py",
    }
    if old_pkg.exists() and old_pkg.is_dir():
        for src_name, dst_name in mapping.items():
            src = old_pkg / src_name
            dst = dex_pkg / dst_name
            if src.exists():
                log.append(
                    f"{'APPLY' if apply else 'PLAN'}: move {src.relative_to(root)} -> {dst.relative_to(root)}"
                )
                if apply:
                    if dst.exists():
                        dst.unlink()
                    shutil.move(str(src), str(dst))
        if apply:
            # remove residual files/dirs
            for leftover in old_pkg.rglob("*"):
                if leftover.is_file():
                    leftover.unlink()
            if old_pkg.exists():
                shutil.rmtree(old_pkg, ignore_errors=True)
            log.append("APPLY: removed zen/pokedex/")

    # Root pokedex/ → dex/
    old_data = root / "pokedex"
    new_data = root / "dex"
    if old_data.exists() and old_data.is_dir():
        log.append(f"{'APPLY' if apply else 'PLAN'}: merge {old_data.name}/ into dex/")
        if apply:
            new_data.mkdir(parents=True, exist_ok=True)
            for item in old_data.iterdir():
                dest = new_data / item.name
                if dest.exists():
                    if dest.is_file() and item.is_file():
                        # prefer newer content from pokedex catalog files
                        dest.unlink()
                    elif dest.is_dir():
                        continue
                shutil.move(str(item), str(dest))
            shutil.rmtree(old_data, ignore_errors=True)

    if apply and not init.exists():
        init.write_text(
            '"""zenOS Dex — catalog, bench, and sync for models/procedures."""\n\n'
            "from zen.dex.catalog import DexCatalog, Tier, get_dex_catalog\n\n"
            '__all__ = ["DexCatalog", "Tier", "get_dex_catalog"]\n',
            encoding="utf-8",
        )
        log.append("APPLY: wrote zen/dex/__init__.py")
    elif not apply:
        log.append("PLAN: write zen/dex/__init__.py")


def archive_legacy_docs(root: Path, apply: bool, log: List[str]) -> None:
    """
    Archive selected historical documentation and create a README identifying current sources of truth.
    
    Parameters:
        root (Path): Repository root containing the documentation files.
        apply (bool): Whether to perform the moves and write the archive README.
        log (List[str]): List receiving planned or completed operation messages.
    """
    archive = root / "docs" / "archive"
    moves = [
        root / "docs" / "zenOS-genesis-log.md",
        root / "docs" / "CONVERSATION_ARCHIVE.md",
        root / "docs" / "STARTER_TEMPLATE.md",
        root / "docs" / "blueprints" / "PROCEDURE-EVOLUTION.md",
    ]
    if apply:
        archive.mkdir(parents=True, exist_ok=True)
    for src in moves:
        if not src.exists():
            continue
        dest = archive / src.name
        log.append(
            f"{'APPLY' if apply else 'PLAN'}: archive {src.relative_to(root)} -> {dest.relative_to(root)}"
        )
        if apply:
            if dest.exists():
                dest.unlink()
            shutil.move(str(src), str(dest))
    readme = archive / "README.md"
    readme_body = (
        "# Archive (historical only)\n\n"
        "These documents are **not** current procedures.\n\n"
        "Current sources of truth:\n"
        "- `dex/` — catalog + protocol index\n"
        "- `docs/GENESIS.md` — philosophy / PCC (Personal Context Core)\n"
        "- `docs/AI_INSTRUCTIONS.md` — agent onboarding\n"
        "- `README.md` — product overview\n"
    )
    if apply:
        readme.write_text(readme_body, encoding="utf-8")
        log.append("APPLY: wrote docs/archive/README.md")
    else:
        log.append("PLAN: write docs/archive/README.md")


def process_file_contents(root: Path, apply: bool) -> Tuple[int, int, List[str]]:
    """
    Apply configured branding and field replacements to eligible repository files.
    
    Parameters:
    	root (Path): Repository root containing files to process.
    	apply (bool): Whether to write transformed content instead of only reporting planned changes.
    
    Returns:
    	Tuple[int, int, List[str]]: The number of changed files, total replacement count, and operation details.
    """
    files_changed = 0
    total_repls = 0
    details: List[str] = []
    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        # Keep the check/rebrand scripts' instructional tokens intact for allowlist purpose;
        # still OK to rewrite other content. Skip rewriting the rebrand script itself heavily —
        # if we rewrite it, allowlist still has the filename. Content with "pokedex" in map is fine.
        if rel in {
            "scripts/rebrand_to_dex.py",
            "scripts/check_no_legacy_branding.py",
            "tests/test_no_legacy_branding.py",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new_text, c1 = replace_text(text)
        c2 = 0
        c3 = 0
        if path.suffix.lower() in {".yaml", ".yml"}:
            new_text, c2 = replace_yaml_fields(new_text)
        if path.suffix.lower() == ".py":
            new_text, c3 = replace_code_fields(new_text)
            # YAML-like fields sometimes appear in py strings already handled
            new_text, extra = replace_yaml_fields(new_text)
            c2 += extra
        total = c1 + c2 + c3
        if total == 0 and new_text == text:
            continue
        if new_text != text:
            files_changed += 1
            total_repls += total
            details.append(f"{'APPLY' if apply else 'PLAN'}: replace x{total} in {rel}")
            write_or_report(path, new_text, apply)
    return files_changed, total_repls, details


def post_fix_catalog(root: Path, apply: bool, log: List[str]) -> None:
    """
    Normalize the Dex catalog module after repository-wide renaming.
    
    Parameters:
        root (Path): Repository root containing ``zen/dex/catalog.py``.
        apply (bool): Whether to write the normalized file instead of only reporting the planned change.
        log (List[str]): List to receive a planned or applied operation message.
    """
    catalog = root / "zen" / "dex" / "catalog.py"
    if not catalog.exists():
        return
    text = catalog.read_text(encoding="utf-8")
    original = text
    # Docstrings / leftover
    text = text.replace("Pokédex", "Dex")
    text = text.replace("pokedex", "dex")
    # Ensure Tier enum exists if Rarity was renamed
    text = text.replace("class Tier(Enum):", "class Tier(Enum):")
    if apply and text != original:
        catalog.write_text(text, encoding="utf-8")
        log.append("APPLY: normalized zen/dex/catalog.py")
    elif text != original:
        log.append("PLAN: normalize zen/dex/catalog.py")


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run the repository rebrand in dry-run or apply mode.
    
    Parameters:
        argv (Sequence[str] | None): Optional command-line arguments. When omitted, arguments are read from the command line.
    
    Returns:
        int: Exit status code, always 0 after processing completes.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    parser.add_argument("--skip-archive", action="store_true", help="Do not move legacy docs")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    apply = args.apply
    log: List[str] = []

    mode = "APPLY" if apply else "DRY-RUN"
    print(f"=== zenOS rebrand [{mode}] root={root} ===")

    ensure_dex_package(root, apply, log)
    if not args.skip_archive:
        archive_legacy_docs(root, apply, log)

    # Content replace: if dry-run before moves, paths still old — so for dry-run we only
    # report path plans + sample. For apply, moves happen first then content replace.
    files_changed, total_repls, details = process_file_contents(root, apply)
    log.extend(details)
    post_fix_catalog(root, apply, log)

    for line in log:
        print(line)
    print(f"--- files_changed={files_changed} replacements≈{total_repls} ops={len(log)} ---")
    if not apply:
        print("Dry-run only. Re-run with --apply to mutate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
