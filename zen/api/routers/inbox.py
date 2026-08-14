"""Inbox HTTP routes."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, Request, status
from pydantic import BaseModel, Field

from zen.api.auth import require_api_token
from zen.api.envelope import make_card, make_collection
from zen.services.inbox import InboxService

router = APIRouter(prefix="/api/v1", tags=["inbox"], dependencies=[Depends(require_api_token)])


class InboxCreateBody(BaseModel):
    """New inbox item."""

    type: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _sid_seq(request: Request) -> tuple[Optional[str], int]:
    sid = request.headers.get("x-zen-session")
    return sid, request.app.state.zen.sessions.next_seq(sid)


def get_inbox_service(request: Request) -> InboxService:
    """Return injected InboxService or construct the default."""
    service = request.app.state.zen.inbox_service
    if service is None:
        service = InboxService()
        request.app.state.zen.inbox_service = service
    return service


@router.get("/cards/inbox")
async def list_inbox(
    request: Request,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    service: InboxService = Depends(get_inbox_service),
) -> dict:
    """List inbox items as zen.inbox.item cards."""
    sid, seq = _sid_seq(request)
    cards = [
        make_card("zen.inbox.item", item["id"], service.item_fields(item))
        for item in service.list_items(status_filter)
    ]
    return make_collection("zen.inbox.item", cards, sid=sid, seq=seq).to_wire()


@router.post("/inbox", status_code=status.HTTP_201_CREATED)
async def create_inbox_item(
    body: InboxCreateBody,
    request: Request,
    service: InboxService = Depends(get_inbox_service),
) -> dict:
    """Capture a new inbox item."""
    sid, seq = _sid_seq(request)
    item = service.add_item(body.type, body.content, body.metadata)
    return make_card(
        "zen.inbox.item", item["id"], service.item_fields(item), sid=sid, seq=seq
    ).to_wire()
