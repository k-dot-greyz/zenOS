import sys
import json
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

from zen.cli_plugins import plugins
from zen.inbox import receive
from zen.utils.template import TemplateEngine, TemplateRegistryError
from zen.templates import TemplatePokedex, TemplateValidator

console = Console()

TEMPLATES_ROOT = Path(__file__).resolve().parents[1] / "templates"
REGISTRY_PATH = TEMPLATES_ROOT / "registry.yaml"
EVOLUTION_PATH = TEMPLATES_ROOT / "metadata" / "evolution.yaml"
SCHEMA_ROOT = TEMPLATES_ROOT / "metadata" / "schemas"

ID_PREFIX_MAP = {
    "documents": "doc",
    "automations": "automation",
    "code": "code",
    "multimedia": "media",
    "metadata": "metadata",
}

FORMAT_EXTENSION_MAP = {
    "markdown": ".md",
    "jinja": ".jinja",
    "yaml": ".yaml",
    "json": ".json",
}


def get_template_engine() -> TemplateEngine:
    return TemplateEngine(template_dir=TEMPLATES_ROOT, registry_path=REGISTRY_PATH)


def get_template_pokedex() -> TemplatePokedex:
    return TemplatePokedex(
        engine=get_template_engine(),
        evolution_path=EVOLUTION_PATH,
    )


def get_template_validator() -> TemplateValidator:
    return TemplateValidator(
        engine=get_template_engine(),
        schema_root=SCHEMA_ROOT,
    )


def load_registry_data() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {"templates": []}
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {"templates": []}


def save_registry_data(data: Dict[str, Any]) -> None:
    data["last_updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    REGISTRY_PATH.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def load_evolution_data() -> Dict[str, Any]:
    if not EVOLUTION_PATH.exists():
        return {"version": "1.0.0", "lineage": {}}
    return yaml.safe_load(EVOLUTION_PATH.read_text(encoding="utf-8")) or {"version": "1.0.0", "lineage": {}}


def save_evolution_data(data: Dict[str, Any]) -> None:
    data["last_updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    EVOLUTION_PATH.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def slugify(value: str) -> str:
    slug = "".join(ch if ch.isalnum() else "_" for ch in value.lower())
    return slug.strip("_")


def generate_template_id(relative_path: Path) -> str:
    parts = list(relative_path.with_suffix("").parts)
    if not parts:
        raise click.ClickException("Invalid template path")
    prefix = ID_PREFIX_MAP.get(parts[0], parts[0])
    remainder = [p.replace("-", "_") for p in parts[1:]]
    components = [prefix] + remainder if remainder else [prefix]
    return ".".join(filter(None, components))


def parse_template_variables(value: Optional[str]) -> Dict[str, Any]:
    if not value:
        return {}

    candidate_path = Path(value)
    if candidate_path.exists():
        content = candidate_path.read_text(encoding="utf-8")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                return yaml.safe_load(content) or {}
            except yaml.YAMLError as exc:
                raise click.ClickException(f"Failed to parse variables file: {exc}") from exc

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return parse_variables(value)


def bump_version(version: str, mode: str) -> str:
    parts = [int(p) for p in (version.split(".") + ["0", "0"])[:3]]
    major, minor, patch = parts
    if mode == "major":
        major += 1
        minor = 0
        patch = 0
    elif mode == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def _generate_template_skeleton(format_name: str, name: str) -> str:
    """Return starter content for a new template based on format."""
    if format_name == "markdown":
        return (
            f"# {name}\n\n"
            "## Summary\n"
            "- {{ summary }}\n\n"
            "## Details\n"
            "{{ details }}\n"
        )
    if format_name == "jinja":
        return (
            "{# " + name + " template #}\n"
            "{% if title %}# {{ title }}{% endif %}\n\n"
            "{{ body }}\n"
        )
    if format_name == "yaml":
        return (
            "title: {{ title }}\n"
            "summary: {{ summary }}\n"
            "items:\n  - {{ item }}\n"
        )
    if format_name == "json":
        return (
            "{\n"
            "  \"title\": \"{{ title }}\",\n"
            "  \"summary\": \"{{ summary }}\",\n"
            "  \"items\": [\"{{ item }}\"]\n"
            "}\n"
        )
    return ""
