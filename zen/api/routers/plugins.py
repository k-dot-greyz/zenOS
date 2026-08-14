"""Plugin card and execute HTTP routes."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from zen.api.auth import require_api_token
from zen.api.envelope import make_card, make_collection
from zen.plugins.executor import ExecutionContext
from zen.services.plugins import PluginService

router = APIRouter(prefix="/api/v1", tags=["plugins"], dependencies=[Depends(require_api_token)])


class PluginExecuteBody(BaseModel):
    """Plugin procedure execution request."""

    procedure_id: str
    input: Any = Field(default_factory=dict)
    user_id: str = "api"


def _sid_seq(request: Request) -> tuple[Optional[str], int]:
    sid = request.headers.get("x-zen-session")
    return sid, request.app.state.zen.sessions.next_seq(sid)


def get_plugin_service(request: Request) -> PluginService:
    """Return injected PluginService or construct the default."""
    service = request.app.state.zen.plugin_service
    if service is None:
        service = PluginService()
        request.app.state.zen.plugin_service = service
    return service


@router.get("/cards/plugins")
async def list_plugins(
    request: Request, service: PluginService = Depends(get_plugin_service)
) -> dict:
    """List installed plugins as zen.plugin cards."""
    sid, seq = _sid_seq(request)
    cards = [
        make_card("zen.plugin", entry.manifest.id, service.plugin_fields(entry))
        for entry in service.list_plugins()
    ]
    return make_collection("zen.plugin", cards, sid=sid, seq=seq).to_wire()


@router.get("/cards/plugins/{plugin_id}")
async def get_plugin(
    plugin_id: str, request: Request, service: PluginService = Depends(get_plugin_service)
) -> dict:
    """Return one zen.plugin card."""
    sid, seq = _sid_seq(request)
    entry = service.get_plugin(plugin_id)
    return make_card(
        "zen.plugin", entry.manifest.id, service.plugin_fields(entry), sid=sid, seq=seq
    ).to_wire()


@router.post("/plugins/{plugin_id}/execute")
async def execute_plugin(
    plugin_id: str,
    body: PluginExecuteBody,
    request: Request,
    service: PluginService = Depends(get_plugin_service),
) -> dict:
    """Execute a plugin procedure and return a zen.execute card."""
    sid, seq = _sid_seq(request)
    context = ExecutionContext(
        user_id=body.user_id,
        session_id=sid or "local",
        device_info={"source": "api"},
    )
    result = await service.execute(plugin_id, body.procedure_id, body.input, context)
    return make_card(
        "zen.execute",
        plugin_id,
        {"status": "done", "result": result.data},
        sid=sid,
        seq=seq,
    ).to_wire()
