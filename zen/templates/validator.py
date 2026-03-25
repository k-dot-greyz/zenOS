"""
Template validation utilities for schema enforcement and linting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from zen.utils.template import TemplateEngine, TemplateRegistryError

try:
    import jsonschema
except ImportError:  # pragma: no cover - jsonschema is optional
    jsonschema = None


PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_\.]+)\s*}}")


@dataclass
class ValidationMessage:
    level: str  # "error" | "warning" | "info"
    message: str


@dataclass
class ValidationReport:
    template_id: str
    is_valid: bool
    messages: List[ValidationMessage] = field(default_factory=list)

    def add(self, level: str, message: str) -> None:
        self.messages.append(ValidationMessage(level=level, message=message))
        if level == "error":
            self.is_valid = False


class TemplateValidator:
    """Validates templates against declared schemas and linting rules."""

    def __init__(
        self,
        engine: Optional[TemplateEngine] = None,
        schema_root: Optional[Path] = None,
    ):
        self.engine = engine or TemplateEngine()
        repo_root = Path(__file__).resolve().parents[1]
        if schema_root is None:
            schema_root = repo_root.parent / "templates" / "metadata" / "schemas"
        self.schema_root = schema_root

    def validate(self, template_id: str, sample_variables: Optional[Dict[str, Any]] = None) -> ValidationReport:
        """
        Validate template correctness using registry metadata.

        Args:
            template_id: Registry id of the template to validate.
            sample_variables: Optional sample payload for render validation.
        """
        report = ValidationReport(template_id=template_id, is_valid=True)

        try:
            entry = self.engine.get_template_entry(template_id)
        except TemplateRegistryError as exc:
            report.add("error", str(exc))
            return report

        self._validate_schema(entry, sample_variables or {}, report)
        self._lint_placeholders(entry, report)
        self._lint_metadata(entry, report)

        if sample_variables:
            self._validate_render(entry, sample_variables, report)

        return report

    # ------------------------------------------------------------------
    # Individual validation passes
    # ------------------------------------------------------------------
    def _validate_schema(self, entry: Dict[str, Any], variables: Dict[str, Any], report: ValidationReport) -> None:
        """Validate variables using JSON schema if available."""
        schema_path = entry.get("compatibility", {}).get("variables_schema")
        if not schema_path:
            report.add("info", "No schema declared; skipping schema validation.")
            return

        schema_file = self.schema_root.parent / schema_path
        if not schema_file.exists():
            report.add("warning", f"Schema file missing: {schema_path}")
            return

        if jsonschema is None:
            report.add(
                "warning",
                "jsonschema package not available; install to enable strict schema validation.",
            )
            return

        schema = jsonschema.Draft7Validator.check_schema(
            jsonschema.load(schema_file.open("r", encoding="utf-8"))
        )
        validator = jsonschema.Draft7Validator(schema)
        errors = sorted(validator.iter_errors(variables), key=lambda e: e.path)
        for error in errors:
            path = ".".join(map(str, error.path)) or "<root>"
            report.add("error", f"Schema violation at {path}: {error.message}")

        if not errors:
            report.add("info", "Schema validation passed.")

    def _lint_placeholders(self, entry: Dict[str, Any], report: ValidationReport) -> None:
        """Warn about unused placeholders in template files."""
        path = entry.get("path")
        if not path:
            report.add("error", "Template entry missing path attribute.")
            return

        try:
            content = self.engine._read_template_file(path)
        except TemplateRegistryError as exc:
            report.add("error", str(exc))
            return

        placeholders = PLACEHOLDER_PATTERN.findall(content)
        if not placeholders:
            report.add("warning", "No Jinja-style placeholders detected.")
            return

        unique = sorted(set(placeholders))
        report.add("info", f"Detected placeholders: {', '.join(unique)}")

    def _lint_metadata(self, entry: Dict[str, Any], report: ValidationReport) -> None:
        """Validate presence of required registry metadata fields."""
        required_fields = ["id", "name", "path", "version"]
        missing = [field for field in required_fields if not entry.get(field)]
        if missing:
            report.add("error", f"Missing required registry fields: {', '.join(missing)}")

        if not entry.get("tags"):
            report.add("warning", "Template has no tags; consider adding for better discovery.")

    def _validate_render(self, entry: Dict[str, Any], variables: Dict[str, Any], report: ValidationReport) -> None:
        """Attempt to render template with provided variables."""
        try:
            self.engine.render_by_id(entry["id"], variables)
        except Exception as exc:  # pylint: disable=broad-except
            report.add("error", f"Render failed with sample data: {exc}")
        else:
            report.add("info", "Render succeeded with provided sample data.")

