"""Agent card and execute HTTP routes."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator, Dict, Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from zen.api.auth import require_api_token
from zen.api.envelope import DeltaEncoder, make_card, make_collection, make_delta, make_done
from zen.services.agents import AgentService

router = APIRouter(prefix="/api/v1", tags=["agents"], dependencies=[Depends(require_api_token)])


class ExecuteBody(BaseModel):
    """Agent execution request."""

    prompt: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    critique: bool = False
    upgrade_only: bool = False


def _sid_seq(request: Request) -> tuple[Optional[str], int]:
    sid = request.headers.get("x-zen-session")
    return sid, request.app.state.zen.sessions.next_seq(sid)


def get_agent_service(request: Request) -> AgentService:
    """Return injected AgentService or construct the default."""
    service = request.app.state.zen.agent_service
    if service is None:
        service = AgentService()
        request.app.state.zen.agent_service = service
    return service


def _agent_fields(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": entry.get("name"),
        "description": entry.get("description"),
        "type": entry.get("type"),
        "version": entry.get("version"),
        "author": entry.get("author"),
        "tags": entry.get("tags"),
    }


def _execute_fields(result: Any) -> Dict[str, Any]:
    if isinstance(result, str):
        return {"status": "done", "text": result}
    return {"status": "done", "result": result}


@router.get("/cards/agents")
async def list_agents(request: Request, service: AgentService = Depends(get_agent_service)) -> dict:
    """List agents as a zen.collection of zen.agent cards."""
    sid, seq = _sid_seq(request)
    cards = [
        make_card("zen.agent", entry["name"], _agent_fields(entry))
        for entry in service.list_agents()
    ]
    return make_collection("zen.agent", cards, sid=sid, seq=seq).to_wire()


@router.get("/cards/agents/{agent_id}")
async def get_agent(
    agent_id: str, request: Request, service: AgentService = Depends(get_agent_service)
) -> dict:
    """Return one zen.agent card."""
    sid, seq = _sid_seq(request)
    entry = service.get_agent(agent_id)
    return make_card("zen.agent", agent_id, _agent_fields(entry), sid=sid, seq=seq).to_wire()


@router.post("/agents/{agent_id}/execute")
async def execute_agent(
    agent_id: str,
    body: ExecuteBody,
    request: Request,
    stream: bool = Query(default=False),
    service: AgentService = Depends(get_agent_service),
) -> Any:
    """Execute an agent; optionally stream deltas over SSE."""
    if stream:
        return EventSourceResponse(
            _stream_execute(request, service, agent_id, body),
            media_type="text/event-stream",
        )
    sid, seq = _sid_seq(request)
    result = await service.execute_async(
        agent_id,
        body.prompt,
        body.variables,
        no_critique=not body.critique,
        upgrade_only=body.upgrade_only,
    )
    return make_card("zen.execute", agent_id, _execute_fields(result), sid=sid, seq=seq).to_wire()


async def _stream_execute(
    request: Request,
    service: AgentService,
    agent_id: str,
    body: ExecuteBody,
) -> AsyncIterator[Dict[str, str]]:
    sid = request.headers.get("x-zen-session")
    encoder = DeltaEncoder()
    seq = request.app.state.zen.sessions.next_seq(sid)
    yield {
        "data": json.dumps(
            make_delta(
                sid,
                seq,
                encoder.delta({"status": "running"}),
                card_type="zen.execute",
                card_id=agent_id,
            ).to_wire()
        )
    }
    result = await service.execute_async(
        agent_id,
        body.prompt,
        body.variables,
        no_critique=not body.critique,
        upgrade_only=body.upgrade_only,
    )
    fields = _execute_fields(result)
    seq = request.app.state.zen.sessions.next_seq(sid)
    yield {
        "data": json.dumps(
            make_delta(
                sid,
                seq,
                encoder.delta(fields),
                card_type="zen.execute",
                card_id=agent_id,
            ).to_wire()
        )
    }
    seq = request.app.state.zen.sessions.next_seq(sid)
    yield {
        "data": json.dumps(make_done(sid, seq, card_id=agent_id, card_type="zen.execute").to_wire())
    }
