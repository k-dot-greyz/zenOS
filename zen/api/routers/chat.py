"""Chat SSE endpoint."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from zen.api.auth import require_api_token
from zen.api.envelope import DeltaEncoder, make_delta, make_done
from zen.services.chat import ChatService

router = APIRouter(prefix="/api/v1", tags=["chat"], dependencies=[Depends(require_api_token)])


class ChatBody(BaseModel):
    """Chat request."""

    message: str
    model: Optional[str] = None


def get_chat_service(request: Request) -> ChatService:
    """Return injected ChatService or the default OpenRouter-backed one."""
    service = request.app.state.zen.chat_service
    if service is None:
        service = ChatService()
        request.app.state.zen.chat_service = service
    return service


@router.post("/chat")
async def chat(
    body: ChatBody,
    request: Request,
    service: ChatService = Depends(get_chat_service),
) -> Any:
    """Stream a chat completion as delta packets over SSE."""
    return EventSourceResponse(
        _stream_chat(request, service, body),
        media_type="text/event-stream",
    )


async def _stream_chat(
    request: Request, service: ChatService, body: ChatBody
) -> AsyncIterator[Dict[str, str]]:
    sid = request.headers.get("x-zen-session")
    chat_id = sid or str(uuid4())
    encoder = DeltaEncoder()
    seq = request.app.state.zen.sessions.next_seq(sid)
    yield {
        "data": json.dumps(
            make_delta(
                sid,
                seq,
                encoder.delta({"status": "running", "model": body.model}),
                card_type="zen.chat",
                card_id=chat_id,
            ).to_wire()
        )
    }
    async for chunk in service.stream(body.message, body.model):
        seq = request.app.state.zen.sessions.next_seq(sid)
        yield {
            "data": json.dumps(
                make_delta(
                    sid,
                    seq,
                    encoder.delta({"text": chunk, "status": "running"}),
                    card_type="zen.chat",
                    card_id=chat_id,
                ).to_wire()
            )
        }
    seq = request.app.state.zen.sessions.next_seq(sid)
    yield {
        "data": json.dumps(
            make_delta(
                sid,
                seq,
                encoder.delta({"status": "done"}),
                card_type="zen.chat",
                card_id=chat_id,
            ).to_wire()
        )
    }
    seq = request.app.state.zen.sessions.next_seq(sid)
    yield {"data": json.dumps(make_done(sid, seq, card_id=chat_id, card_type="zen.chat").to_wire())}
