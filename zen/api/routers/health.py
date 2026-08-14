"""Health and version routers."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from zen import __version__
from zen.api.auth import require_api_token
from zen.api.envelope import CAPABILITIES, SCHEMA_ID, make_card

health_router = APIRouter(tags=["health"])
meta_router = APIRouter(prefix="/api/v1", tags=["meta"], dependencies=[Depends(require_api_token)])


@health_router.get("/health")
async def health() -> dict:
    """Liveness probe; unauthenticated by design."""
    return {"status": "ok", "version": __version__}


@meta_router.get("/meta")
async def meta(request: Request) -> dict:
    """Advertise API version, schema id, and capabilities."""
    sid = request.headers.get("x-zen-session")
    seq = request.app.state.zen.sessions.next_seq(sid)
    packet = make_card(
        "zen.meta",
        "zenos",
        {
            "version": __version__,
            "schema_id": SCHEMA_ID,
            "capabilities": list(CAPABILITIES),
        },
        sid=sid,
        seq=seq,
    )
    return packet.to_wire()
