"""
Template engine for zenOS using Jinja2 with registry integration.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

import yaml
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape


class TemplateRegistryError(RuntimeError):
    """Raised when a template cannot be discovered or rendered."""


class TemplateEngine:
    """
    Jinja2-based template engine for rendering prompts and content with
    Template Pokédex registry integration.
    """

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        registry_path: Optional[Path] = None,
    ):
        """Initialize the template engine with registry-aware configuration."""
        repo_root = Path(__file__).resolve().parents[2]
        if template_dir is None:
            template_dir = repo_root / "templates"
        if registry_path is None:
            registry_path = template_dir / "registry.yaml"

        self.template_dir = template_dir
        self.registry_path = registry_path
        self._registry_meta: Dict[str, Any] = {}
        self._registry_index: Dict[str, Dict[str, Any]] = {}

        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)) if template_dir.exists() else None,
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters and globals early
        self.env.filters["markdown"] = self._markdown_filter
        self.env.filters["code"] = self._code_filter
        self.env.globals["include_template"] = self.render_by_id

        self._load_registry()

    # ------------------------------------------------------------------
    # Registry operations
    # ------------------------------------------------------------------
    def _load_registry(self) -> None:
        """Load and index the template registry file."""
        if not self.registry_path.exists():
            raise TemplateRegistryError(
                f"Template registry not found at {self.registry_path}"
            )

        data = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
        templates = data.get("templates", [])
        self._registry_meta = {k: v for k, v in data.items() if k != "templates"}
        self._registry_index = {entry["id"]: entry for entry in templates}

    def refresh_registry(self) -> None:
        """Reload registry from disk."""
        self._load_registry()

    def get_registry_meta(self) -> Dict[str, Any]:
        """Return registry metadata (version, maintainer, etc.)."""
        return dict(self._registry_meta)

    def list_templates(self, *, tags: Optional[Iterable[str]] = None) -> Iterable[Dict[str, Any]]:
        """
        Iterate templates optionally filtered by tags.

        Args:
            tags: Optional tag collection to filter by.
        """
        if not tags:
            return list(self._registry_index.values())

        tag_set = set(tags)
        return [
            entry
            for entry in self._registry_index.values()
            if tag_set.intersection(entry.get("tags", []))
        ]

    def get_template_entry(self, template_id: str) -> Dict[str, Any]:
        """Retrieve raw registry entry for a template id."""
        try:
            return self._registry_index[template_id]
        except KeyError as exc:
            raise TemplateRegistryError(f"Unknown template id: {template_id}") from exc

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def render(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render an ad-hoc template string with variables."""
        template = Template(template_str)
        return template.render(**variables)

    def render_file(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Render a template file using the Jinja environment."""
        if not self.env.loader:
            raise TemplateRegistryError("No template directory configured for rendering.")

        normalized_name = self._normalize_template_name(template_name)
        template = self.env.get_template(normalized_name)
        return template.render(**variables)

    def render_by_id(self, template_id: str, variables: Dict[str, Any]) -> str:
        """
        Render a template using its registry entry.

        Supports Jinja templates, raw text, markdown, and JSON content.
        """
        entry = self.get_template_entry(template_id)
        self._validate_variables(entry, variables)

        template_path = entry.get("path")
        if not template_path:
            raise TemplateRegistryError(f"Template '{template_id}' missing path information.")

        template_type = entry.get("type", "").lower()
        if template_type in {"jinja", "jinja2"} or template_path.endswith((".j2", ".jinja")):
            return self.render_file(template_path, variables)

        if template_type in {"markdown", "md"} or template_path.endswith(".md"):
            content = self._read_template_file(template_path)
            return self.render(content, variables)

        if template_type in {"yaml", "yml", "json"}:
            content = self._read_template_file(template_path)
            rendered = self.render(content, variables)
            if template_type == "json":
                json.loads(rendered)  # ensure valid JSON after rendering
            return rendered

        # Default: treat as plain text
        content = self._read_template_file(template_path)
        return self.render(content, variables)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def read_template_source(self, relative_path: str) -> str:
        """Public accessor for raw template source."""
        return self._read_template_file(relative_path)

    def _normalize_template_name(self, template_name: str) -> str:
        """Normalize template path to Jinja loader expectations."""
        return template_name.replace("\\", "/")

    def _read_template_file(self, relative_path: str) -> str:
        """Read a template file relative to the template directory."""
        file_path = self.template_dir / relative_path
        if not file_path.exists():
            raise TemplateRegistryError(f"Template file not found: {relative_path}")
        return file_path.read_text(encoding="utf-8")

    def _validate_variables(self, entry: Dict[str, Any], variables: Dict[str, Any]) -> None:
        """
        Basic variable validation using registry metadata.

        - Ensures required variables are present
        - Provides hints for missing optional blocks
        """
        requirements = entry.get("requirements", {})
        required_vars = requirements.get("required_variables", [])
        missing = [var for var in required_vars if var not in variables]
        if missing:
            raise TemplateRegistryError(
                f"Template '{entry['id']}' missing required variables: {', '.join(missing)}"
            )

        # Optional schema reference recorded for downstream validation
        schema_path = entry.get("compatibility", {}).get("variables_schema")
        if schema_path and not (self.template_dir / schema_path).exists():
            # Defer schema enforcement to validator subsystem; warn in debug logs
            pass

    def _markdown_filter(self, text: str) -> str:
        """Convert text to markdown block format."""
        return f"```markdown\n{text}\n```"

    def _code_filter(self, text: str, language: str = "python") -> str:
        """Format text as code block."""
        return f"```{language}\n{text}\n```"
