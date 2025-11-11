"""
Template Pokédex - discovery, cataloging, and analytics for the template registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

from zen.utils.template import TemplateEngine, TemplateRegistryError


@dataclass(frozen=True)
class TemplateRecord:
    """Normalized representation of a template registry entry."""

    id: str
    name: str
    path: str
    type: str
    tags: List[str]
    version: str
    rarity: str
    usage_count: int
    metadata: Dict[str, Any]
    evolution: Dict[str, Any]


class TemplatePokedex:
    """
    High-level facade around TemplateEngine providing template discovery,
    rarity calculation, evolution tracking, and usage analytics.
    """

    def __init__(
        self,
        engine: Optional[TemplateEngine] = None,
        evolution_path: Optional[Path] = None,
    ):
        self.engine = engine or TemplateEngine()
        repo_root = Path(__file__).resolve().parents[1]
        if evolution_path is None:
            evolution_path = repo_root.parent / "templates" / "metadata" / "evolution.yaml"

        self.evolution_path = evolution_path
        self._evolution_index = self._load_evolution(evolution_path)

    # ------------------------------------------------------------------
    # Loading and indexing
    # ------------------------------------------------------------------
    def _load_evolution(self, path: Path) -> Dict[str, Dict[str, Any]]:
        if not path.exists():
            raise TemplateRegistryError(f"Evolution tracker not found at {path}")

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return data.get("lineage", {})

    def refresh(self) -> None:
        """Refresh registry and evolution metadata."""
        self.engine.refresh_registry()
        self._evolution_index = self._load_evolution(self.evolution_path)

    # ------------------------------------------------------------------
    # Catalog operations
    # ------------------------------------------------------------------
    def catalog(self, *, tags: Optional[Iterable[str]] = None) -> List[TemplateRecord]:
        """Return catalog of templates optionally filtered by tags."""
        entries = self.engine.list_templates(tags=tags)
        return [self._to_record(entry) for entry in entries]

    def get(self, template_id: str) -> TemplateRecord:
        """Retrieve a single template record by id."""
        entry = self.engine.get_template_entry(template_id)
        return self._to_record(entry)

    def exists(self, template_id: str) -> bool:
        """Check if template id exists in the registry."""
        try:
            self.engine.get_template_entry(template_id)
        except TemplateRegistryError:
            return False
        return True

    # ------------------------------------------------------------------
    # Analytics and evolution
    # ------------------------------------------------------------------
    def get_usage_summary(self, template_id: str) -> Dict[str, Any]:
        """Return usage analytics for the template."""
        record = self.get(template_id)
        usage = record.metadata.get("usage", {})
        return {
            "usage_count": usage.get("usage_count", 0),
            "last_used": usage.get("last_used"),
            "average_render_time_ms": usage.get("average_render_time_ms"),
            "rarity": record.rarity,
            "recommended_evolution": self.suggest_evolution(template_id),
        }

    def get_evolution_history(self, template_id: str) -> Dict[str, Any]:
        """Return evolution history for a template."""
        return self._evolution_index.get(template_id, {})

    def suggest_evolution(self, template_id: str) -> Optional[str]:
        """
        Provide evolution suggestion based on usage and lineage.

        Returns human-readable suggestion string or None.
        """
        record = self.get(template_id)
        usage = record.metadata.get("usage", {})
        evolution_meta = self.get_evolution_history(template_id)

        if not evolution_meta:
            return None

        current_version = evolution_meta.get("current_version")
        history = evolution_meta.get("history", [])
        last_entry = history[-1] if history else None
        usage_count = usage.get("usage_count", 0)

        if usage_count > 100 and record.rarity in {"common", "uncommon"}:
            return (
                f"High usage detected ({usage_count}). "
                f"Consider evolving '{template_id}' to incorporate advanced variants."
            )

        if last_entry and last_entry.get("breaking"):
            return (
                f"Latest version {current_version} introduced breaking changes. "
                "Review dependent automation for compatibility."
            )

        successor = evolution_meta.get("deprecation", {}).get("successor")
        if successor:
            return f"Template deprecated. Migrate usage to successor '{successor}'."

        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _to_record(self, entry: Dict[str, Any]) -> TemplateRecord:
        template_id = entry["id"]
        evolution = self._evolution_index.get(template_id, {})
        usage = entry.get("usage", {})
        rarity = self._calculate_rarity(entry, usage)

        return TemplateRecord(
            id=template_id,
            name=entry.get("name", template_id),
            path=entry.get("path"),
            type=entry.get("type", "text"),
            tags=list(entry.get("tags", [])),
            version=entry.get("version", "0.0.0"),
            rarity=rarity,
            usage_count=usage.get("usage_count", 0),
            metadata=entry,
            evolution=evolution,
        )

    def _calculate_rarity(self, entry: Dict[str, Any], usage: Dict[str, Any]) -> str:
        """Calculate rarity dynamically using usage, versioning, and tags."""
        base_rarity = entry.get("rarity")
        if base_rarity:
            return base_rarity

        usage_count = usage.get("usage_count", 0)
        tags = set(entry.get("tags", []))

        if usage_count > 500 or "critical" in tags:
            return "legendary"
        if usage_count > 100 or "automation" in tags:
            return "epic"
        if usage_count > 25 or "ai-generated" in tags:
            return "rare"
        if usage_count > 5:
            return "uncommon"
        return "common"

