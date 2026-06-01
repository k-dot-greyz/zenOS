#!/usr/bin/env python3
"""Merge core a11y manifest with optional extension YAML/MD files."""

from __future__ import annotations

import argparse
import copy
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

SKILL_ROOT = Path(__file__).resolve().parents[1]
CORE_MANIFEST = SKILL_ROOT / "core-manifest.yaml"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return data


def load_extension(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".md", ".markdown"}:
        match = FRONTMATTER_RE.match(text)
        if not match:
            raise ValueError(f"{path}: markdown extension requires YAML frontmatter")
        return yaml.safe_load(match.group(1)) or {}
    return load_yaml(path)


def spec_index(specs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {s["id"]: s for s in specs if isinstance(s, dict) and "id" in s}


def merge_specs(base: list[dict[str, Any]], extra: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = copy.deepcopy(base)
    by_id = spec_index(merged)
    for spec in extra:
        if not isinstance(spec, dict) or "id" not in spec:
            continue
        sid = spec["id"]
        if sid in by_id:
            target = by_id[sid]
            for key, value in spec.items():
                if key == "checkpoints" and "checkpoints" in target:
                    existing = target.setdefault("checkpoints", [])
                    existing.extend(value or [])
                elif key == "related" and "related" in target:
                    target.setdefault("related", []).extend(value or [])
                else:
                    target[key] = value
        else:
            merged.append(copy.deepcopy(spec))
            by_id[sid] = merged[-1]
    return merged


def merge_common_suspects(base: list[dict[str, Any]], extra: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not extra:
        return base
    seen = {c.get("id") for c in base if isinstance(c, dict)}
    out = copy.deepcopy(base)
    for item in extra:
        if isinstance(item, dict) and item.get("id") not in seen:
            out.append(item)
            seen.add(item.get("id"))
    return out


def merge_manifest(
    core: dict[str, Any],
    extensions: list[dict[str, Any]],
    *,
    target: str | None,
    output_dir: str | None,
    spec_filter: list[str] | None,
) -> dict[str, Any]:
    result = copy.deepcopy(core)
    result["extensions_merged"] = []

    for ext in extensions:
        source = ext.pop("_source", "unknown")
        result["extensions_merged"].append(source)
        if "default_conformance" in ext:
            result.setdefault("default_conformance", {}).update(ext["default_conformance"])
        if "specs" in ext:
            result["specs"] = merge_specs(result.get("specs", []), ext["specs"] or [])
        if "common_suspects" in ext:
            result["common_suspects"] = merge_common_suspects(
                result.get("common_suspects", []), ext["common_suspects"] or []
            )

    if target:
        result["audit"] = {"target": target}
    if output_dir:
        result["audit"] = result.get("audit", {})
        result["audit"]["output_dir"] = output_dir

    if spec_filter:
        allowed = set(spec_filter)
        result["specs"] = [s for s in result.get("specs", []) if s.get("id") in allowed]

    return result


def write_report_stubs(manifest: dict[str, Any], out_dir: Path) -> None:
    """Create placeholder report files if missing (agent replaces content)."""
    template_path = SKILL_ROOT / "report-template.md"
    stub_notice = (
        "<!-- Generated stub — replace with audit findings per "
        "report-template.md -->\n\n"
        "_Audit pending. Run the a11y-compliance-audit skill against the target._\n"
    )
    for spec in manifest.get("specs", []):
        report_name = spec.get("report_file") or f"{spec['id']}.md"
        report_path = out_dir / report_name
        if not report_path.exists():
            title = spec.get("title", spec["id"])
            report_path.write_text(f"# {title}\n\n{stub_notice}", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge core + extension a11y audit manifests")
    parser.add_argument("--core", type=Path, default=CORE_MANIFEST, help="Core manifest path")
    parser.add_argument(
        "--extension",
        action="append",
        default=[],
        type=Path,
        help="Extension YAML or MD (repeatable)",
    )
    parser.add_argument("--target", help="Audit target (URL or path)")
    parser.add_argument("--output-dir", required=True, help="Report output directory")
    parser.add_argument(
        "--specs",
        nargs="*",
        help="Only include these spec ids (e.g. wcag-22 aria-apg)",
    )
    parser.add_argument(
        "--write-stubs",
        action="store_true",
        help="Create empty per-spec .md stubs if missing",
    )
    args = parser.parse_args()

    core = load_yaml(args.core)
    extensions: list[dict[str, Any]] = []
    for path in args.extension:
        if not path.exists():
            print(f"warning: extension not found: {path}", file=sys.stderr)
            continue
        data = load_extension(path)
        data["_source"] = str(path)
        extensions.append(data)

    merged = merge_manifest(
        core,
        extensions,
        target=args.target,
        output_dir=args.output_dir,
        spec_filter=args.specs,
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    merged_path = out_dir / "manifest.merged.yaml"
    with merged_path.open("w", encoding="utf-8") as f:
        yaml.dump(merged, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    readme = out_dir / "README.md"
    if not readme.exists():
        lines = [
            "# Accessibility audit rollup",
            "",
            f"**Target:** {args.target or '(not set)'}",
            "",
            "## Spec reports",
            "",
        ]
        for spec in merged.get("specs", []):
            report = spec.get("report_file", f"{spec['id']}.md")
            title = spec.get("title", spec["id"])
            url = spec.get("normative_url", "")
            lines.append(f"- [{title}](./{report}) — [{url}]({url})")
        lines.extend(["", "## Manifest", "", f"Composed pipe: [`manifest.merged.yaml`](./manifest.merged.yaml)", ""])
        readme.write_text("\n".join(lines), encoding="utf-8")

    if args.write_stubs:
        write_report_stubs(merged, out_dir)

    print(merged_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
