"""Dex model and procedure HTTP routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from zen.api.auth import require_api_token
from zen.api.envelope import make_card, make_collection
from zen.services.dex import DexService

router = APIRouter(prefix="/api/v1", tags=["dex"], dependencies=[Depends(require_api_token)])


def _sid_seq(request: Request) -> tuple[Optional[str], int]:
    sid = request.headers.get("x-zen-session")
    return sid, request.app.state.zen.sessions.next_seq(sid)


def get_dex_service(request: Request) -> DexService:
    """Return injected DexService or construct the default catalog service."""
    service = request.app.state.zen.dex_service
    if service is None:
        service = DexService()
        request.app.state.zen.dex_service = service
    return service


@router.get("/cards/models")
async def list_models(
    request: Request,
    tier: Optional[str] = Query(default=None),
    task: Optional[str] = Query(default=None),
    service: DexService = Depends(get_dex_service),
) -> dict:
    """List Dex models as zen.model cards."""
    sid, seq = _sid_seq(request)
    cards = [
        make_card("zen.model", model.id, service.model_fields(model))
        for model in service.list_models(tier=tier, task=task)
    ]
    return make_collection("zen.model", cards, sid=sid, seq=seq).to_wire()


@router.get("/cards/models/{model_id:path}")
async def get_model(
    model_id: str, request: Request, service: DexService = Depends(get_dex_service)
) -> dict:
    """Return one zen.model card."""
    sid, seq = _sid_seq(request)
    model = service.get_model(model_id)
    return make_card("zen.model", model.id, service.model_fields(model), sid=sid, seq=seq).to_wire()


@router.get("/cards/procedures")
async def list_procedures(
    request: Request,
    type: Optional[str] = Query(default=None, alias="type"),
    tier: Optional[str] = Query(default=None),
    service: DexService = Depends(get_dex_service),
) -> dict:
    """List Dex procedures as zen.procedure cards."""
    sid, seq = _sid_seq(request)
    cards = [
        make_card("zen.procedure", procedure.id, service.procedure_fields(procedure))
        for procedure in service.list_procedures(proc_type=type, tier=tier)
    ]
    return make_collection("zen.procedure", cards, sid=sid, seq=seq).to_wire()


@router.get("/cards/procedures/{procedure_id}")
async def get_procedure(
    procedure_id: str, request: Request, service: DexService = Depends(get_dex_service)
) -> dict:
    """Return one zen.procedure card."""
    sid, seq = _sid_seq(request)
    procedure = service.get_procedure(procedure_id)
    return make_card(
        "zen.procedure",
        procedure.id,
        service.procedure_fields(procedure),
        sid=sid,
        seq=seq,
    ).to_wire()


@router.get("/dex/stats")
async def dex_stats(request: Request, service: DexService = Depends(get_dex_service)) -> dict:
    """Return Dex collection statistics."""
    sid, seq = _sid_seq(request)
    return make_card("zen.dex.stats", "dex", service.stats(), sid=sid, seq=seq).to_wire()


@router.post("/dex/sync")
async def dex_sync(
    request: Request,
    force: bool = Query(default=False),
    service: DexService = Depends(get_dex_service),
) -> dict:
    """Sync Dex from OpenRouter and return updated stats."""
    sid, seq = _sid_seq(request)
    stats = await service.sync(force=force)
    return make_card("zen.dex.stats", "dex", stats, sid=sid, seq=seq).to_wire()
