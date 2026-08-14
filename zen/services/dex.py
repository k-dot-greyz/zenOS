"""Dex catalog use cases shared by CLI and HTTP."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from zen.dex.catalog import DexCatalog, ModelEntry, ProcedureEntry, Tier
from zen.services.errors import NotFoundError, ServiceError


class DexService:
    """Read models/procedures from the Dex catalog."""

    def __init__(self, catalog: Optional[DexCatalog] = None, syncer: Any = None) -> None:
        self.catalog = catalog or DexCatalog()
        self._syncer = syncer

    def _tier(self, value: Optional[str]) -> Optional[Tier]:
        if value is None:
            return None
        try:
            return Tier(value)
        except ValueError as exc:
            raise ServiceError(
                f"Unknown tier: {value}",
                code="validation_error",
                status_code=422,
                details={"tier": value},
            ) from exc

    def model_fields(self, model: ModelEntry) -> Dict[str, Any]:
        """Serialize a model entry to card fields."""
        return {
            "name": model.name,
            "provider": model.provider,
            "type": model.type,
            "tier": model.tier.value,
            "stats": model.stats,
            "feats": model.feats,
            "best_for": model.best_for,
            "context_window": model.context_window,
            "cost_per_1k": model.cost_per_1k,
        }

    def procedure_fields(self, procedure: ProcedureEntry) -> Dict[str, Any]:
        """Serialize a procedure entry to card fields."""
        return {
            "name": procedure.name,
            "type": procedure.type,
            "tier": procedure.tier.value,
            "stats": procedure.stats,
            "requirements": procedure.requirements,
            "discovered_by": procedure.discovered_by,
            "usage_count": procedure.usage_count,
        }

    def list_models(self, *, tier: Optional[str] = None, task: Optional[str] = None) -> List[ModelEntry]:
        """List models, optionally filtered by tier or task."""
        if task:
            models = self.catalog.find_model_for_task(task)
        elif tier:
            models = self.catalog.get_models_by_tier(self._tier(tier))
        else:
            models = list(self.catalog.models.values())
        if tier and task:
            wanted = self._tier(tier)
            models = [model for model in models if model.tier == wanted]
        return models

    def get_model(self, model_id: str) -> ModelEntry:
        """Return one model or raise NotFoundError."""
        model = self.catalog.models.get(model_id)
        if model is None:
            raise NotFoundError(f"Model not found: {model_id}", details={"id": model_id})
        return model

    def list_procedures(
        self, *, proc_type: Optional[str] = None, tier: Optional[str] = None
    ) -> List[ProcedureEntry]:
        """List procedures, optionally filtered by type or tier."""
        procedures = list(self.catalog.procedures.values())
        if proc_type:
            procedures = [item for item in procedures if item.type == proc_type]
        if tier:
            wanted = self._tier(tier)
            procedures = [item for item in procedures if item.tier == wanted]
        return procedures

    def get_procedure(self, procedure_id: str) -> ProcedureEntry:
        """Return one procedure or raise NotFoundError."""
        procedure = self.catalog.procedures.get(procedure_id)
        if procedure is None:
            raise NotFoundError(
                f"Procedure not found: {procedure_id}", details={"id": procedure_id}
            )
        return procedure

    def stats(self) -> Dict[str, Any]:
        """Return Dex collection statistics."""
        return self.catalog.calculate_collection_stats()

    async def sync(self, *, force: bool = False) -> Dict[str, Any]:
        """Refresh Dex from OpenRouter (or an injected syncer) and return stats."""
        syncer = self._syncer
        if syncer is None:
            from zen.dex.openrouter_sync import OpenRouterSync

            syncer = OpenRouterSync()
            self._syncer = syncer
        if force:
            cache_file = getattr(syncer, "cache_file", None)
            if cache_file is not None and getattr(cache_file, "exists", lambda: False)():
                cache_file.unlink()
        await syncer.sync_dex()
        self.catalog.load_data()
        return self.stats()
