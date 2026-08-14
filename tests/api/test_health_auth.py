"""Health, meta, session handshake, and Bearer auth."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from starlette.middleware.cors import CORSMiddleware

from zen.api.app import create_app
from zen.api.auth import is_loopback_host, require_token_for_bind
from zen.api.envelope import SCHEMA_ID, handshake_schema


def test_health_is_public_even_with_token_configured():
    client = TestClient(create_app(api_token="secret"))
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_meta_open_when_no_token_configured():
    client = TestClient(create_app(api_token=None))
    response = client.get("/api/v1/meta")
    assert response.status_code == 200
    packet = response.json()
    assert packet["kind"] == "card"
    assert packet["type"] == "zen.meta"
    assert packet["fields"]["schema_id"] == SCHEMA_ID
    assert "agents" in packet["fields"]["capabilities"]


def test_protected_route_401_without_bearer_when_token_set():
    client = TestClient(create_app(api_token="secret"))
    response = client.get("/api/v1/meta")
    assert response.status_code == 401
    packet = response.json()
    assert packet["kind"] == "error"
    assert packet["type"] == "zen.error"
    assert packet["fields"]["code"] == "unauthorized"
    assert "detail" not in packet


def test_protected_route_ok_with_bearer_token():
    client = TestClient(create_app(api_token="secret"))
    response = client.get("/api/v1/meta", headers={"Authorization": "Bearer secret"})
    assert response.status_code == 200
    assert response.json()["type"] == "zen.meta"


def test_invalid_bearer_token_is_unauthorized():
    client = TestClient(create_app(api_token="secret"))
    response = client.get("/api/v1/meta", headers={"Authorization": "Bearer nope"})
    assert response.status_code == 401
    assert response.json()["fields"]["code"] == "unauthorized"


def test_session_handshake_returns_schema_dump():
    client = TestClient(create_app(api_token=None))
    response = client.post("/api/v1/session")
    assert response.status_code == 201
    packet = response.json()
    assert packet["kind"] == "card"
    assert packet["type"] == "zen.session"
    sid = packet["sid"]
    assert sid
    assert packet["id"] == sid
    fields = packet["fields"]
    expected = handshake_schema()
    assert fields["schema_id"] == expected["schema_id"]
    assert fields["packet_kinds"] == expected["packet_kinds"]
    assert "zen.agent" in fields["card_types"]
    assert "name" in fields["card_types"]["zen.agent"]["fields"]
    assert "agents" in fields["capabilities"]


def test_unknown_route_returns_zen_error_packet():
    client = TestClient(create_app(api_token=None))
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    packet = response.json()
    assert packet["kind"] == "error"
    assert packet["type"] == "zen.error"
    assert packet["fields"]["code"] == "not_found"


def test_cors_allowlist_is_not_wildcard():
    app = create_app()
    cors = [m for m in app.user_middleware if m.cls is CORSMiddleware]
    assert cors
    origins = cors[0].kwargs.get("allow_origins") or []
    assert "*" not in origins
    assert "http://localhost:3000" in origins


def test_loopback_bind_allows_missing_token():
    require_token_for_bind("127.0.0.1", None)
    require_token_for_bind("localhost", "optional")
    assert is_loopback_host("127.0.0.1")
    assert is_loopback_host("::1")
    assert not is_loopback_host("0.0.0.0")


def test_non_loopback_bind_requires_token():
    with pytest.raises(ValueError, match="ZEN_API_TOKEN"):
        require_token_for_bind("0.0.0.0", None)
    with pytest.raises(ValueError, match="ZEN_API_TOKEN"):
        require_token_for_bind("192.168.1.10", "")
    require_token_for_bind("0.0.0.0", "secret")
