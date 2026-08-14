"""Chat SSE endpoint."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from zen.api.app import create_app
from zen.api.state import ApiState
from zen.services.chat import ChatService


async def _fake_completer(message: str, model: str | None):
    for part in ("Hel", "lo"):
        yield part


def test_chat_streams_deltas_then_done():
    service = ChatService(completer=_fake_completer)
    client = TestClient(
        create_app(api_token=None, state=ApiState(api_token=None, chat_service=service))
    )
    with client.stream("POST", "/api/v1/chat", json={"message": "hi"}) as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())
    kinds = []
    texts = []
    for line in body.splitlines():
        if not line.startswith("data: "):
            continue
        payload = json.loads(line[6:])
        kinds.append(payload["kind"])
        if payload["kind"] == "delta" and "text" in payload.get("fields", {}):
            texts.append(payload["fields"]["text"])
    assert texts == ["Hel", "lo"]
    assert kinds[-1] == "done"
    assert "delta" in kinds
