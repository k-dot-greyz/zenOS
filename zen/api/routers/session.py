"""Session handshake router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

from zen.api.auth import require_api_token
from zen.api.envelope import handshake_schema, make_card

router = APIRouter(
    prefix="/api/v1", tags=["session"], dependencies=[Depends(require_api_token)]
)


@router.post("/session", status_code=status.HTTP_201_CREATED)
async def create_session(request: Request) -> dict:
    """Handshake: allocate a session id and dump the packet schema."""
    sid = request.app.state.zen.sessions.create()
    schema = handshake_schema()
    packet = make_card("zen.session", sid, schema, sid=sid, seq=0)
    return packet.to_wire()
