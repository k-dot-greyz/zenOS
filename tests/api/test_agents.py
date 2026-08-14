"""AgentService and /api/v1 agent card/execute endpoints."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from zen.api.app import create_app
from zen.api.state import ApiState
from zen.core.agent import AgentManifest
from zen.services.agents import AgentService
from zen.services.errors import NotFoundError


class _FakeAgent:
    def __init__(self, name: str, description: str = "test agent") -> None:
        self.manifest = AgentManifest(
            name=name,
            description=description,
            version="1.0.0",
            author="tests",
            tags=["test"],
        )

    def execute(self, prompt: str, variables: dict) -> str:
        extra = variables.get("k", "")
        return f"{self.manifest.name}:{prompt}:{extra}"


class _FakeRegistry:
    def __init__(self, agents: list[_FakeAgent]) -> None:
        self._agents = {agent.manifest.name: agent for agent in agents}

    def list_agents(self) -> list[dict]:
        return [
            {
                "name": agent.manifest.name,
                "description": agent.manifest.description,
                "type": "custom",
                "version": agent.manifest.version,
                "author": agent.manifest.author,
                "tags": agent.manifest.tags,
            }
            for agent in self._agents.values()
        ]

    def get_agent(self, name: str) -> _FakeAgent:
        if name not in self._agents:
            raise ValueError(f"Agent not found: {name}")
        return self._agents[name]


def _service() -> AgentService:
    registry = _FakeRegistry([_FakeAgent("echo", "echoes prompts")])
    return AgentService(registry=registry)


def _client(service: AgentService | None = None) -> TestClient:
    svc = service or _service()
    return TestClient(create_app(api_token=None, state=ApiState(api_token=None, agent_service=svc)))


def test_agent_service_list_and_get():
    service = _service()
    listed = service.list_agents()
    assert listed[0]["name"] == "echo"
    assert service.get_agent("echo")["description"] == "echoes prompts"
    try:
        service.get_agent("missing")
        assert False, "expected NotFoundError"
    except NotFoundError as exc:
        assert exc.code == "not_found"
        assert exc.status_code == 404


def test_agent_service_execute():
    service = _service()
    import asyncio

    result = asyncio.run(service.execute_async("echo", "hello", {"k": "x"}, no_critique=True))
    assert result == "echo:hello:x"


def test_list_agent_cards():
    response = _client().get("/api/v1/cards/agents")
    assert response.status_code == 200
    packet = response.json()
    assert packet["type"] == "zen.collection"
    assert packet["fields"]["item_type"] == "zen.agent"
    assert packet["fields"]["count"] == 1
    assert packet["fields"]["items"][0]["id"] == "echo"
    assert packet["fields"]["items"][0]["fields"]["name"] == "echo"


def test_get_agent_card():
    response = _client().get("/api/v1/cards/agents/echo")
    assert response.status_code == 200
    packet = response.json()
    assert packet["kind"] == "card"
    assert packet["type"] == "zen.agent"
    assert packet["id"] == "echo"
    assert packet["fields"]["version"] == "1.0.0"


def test_execute_unknown_agent_is_zen_error_404():
    response = _client().post("/api/v1/agents/nope/execute", json={"prompt": "hi"})
    assert response.status_code == 404
    packet = response.json()
    assert packet["kind"] == "error"
    assert packet["type"] == "zen.error"
    assert packet["fields"]["code"] == "not_found"
    assert packet["fields"]["details"]["id"] == "nope"


def test_execute_agent_returns_execute_card():
    response = _client().post(
        "/api/v1/agents/echo/execute",
        json={"prompt": "hi", "variables": {"k": "z"}},
    )
    assert response.status_code == 200
    packet = response.json()
    assert packet["type"] == "zen.execute"
    assert packet["id"] == "echo"
    assert packet["fields"]["status"] == "done"
    assert packet["fields"]["text"] == "echo:hi:z"


def test_execute_agent_stream_emits_delta_then_done():
    with _client().stream(
        "POST",
        "/api/v1/agents/echo/execute?stream=true",
        json={"prompt": "hi"},
    ) as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())
    kinds = []
    for line in body.splitlines():
        if not line.startswith("data: "):
            continue
        payload = json.loads(line[6:])
        kinds.append(payload["kind"])
        if payload["kind"] == "delta" and "text" in payload.get("fields", {}):
            assert payload["fields"]["text"] == "echo:hi:"
    assert "delta" in kinds
    assert kinds[-1] == "done"
