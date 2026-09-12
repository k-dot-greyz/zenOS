"""PluginService and inbox card endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from zen.api.app import create_app
from zen.api.state import ApiState
from zen.plugins.executor import ExecutionResult
from zen.services.inbox import InboxService
from zen.services.plugins import PluginService


class _Manifest:
    id = "com.example.text"
    name = "Text"
    version = "1.0.0"
    author = "tests"
    description = "text plugin"
    category = "text-processing"
    capabilities = ["text_processing"]


class _Entry:
    manifest = _Manifest()
    is_active = True
    usage_count = 3


class _Registry:
    def __init__(self) -> None:
        self.plugins = {_Entry.manifest.id: _Entry()}

    def get_plugin(self, plugin_id: str):
        return self.plugins.get(plugin_id)


class _Executor:
    async def execute_plugin(self, plugin_id, procedure_id, input_data, context):
        if plugin_id != "com.example.text":
            return ExecutionResult(success=False, data=None, error=f"Plugin {plugin_id} not found")
        if procedure_id != "run":
            return ExecutionResult(
                success=False, data=None, error=f"Procedure {procedure_id} not found"
            )
        return ExecutionResult(success=True, data={"echo": input_data}, error=None, metadata={})


def _plugin_client() -> TestClient:
    service = PluginService(registry=_Registry(), executor=_Executor())
    return TestClient(
        create_app(api_token=None, state=ApiState(api_token=None, plugin_service=service))
    )


def test_list_and_get_plugin_cards():
    client = _plugin_client()
    listed = client.get("/api/v1/cards/plugins")
    assert listed.status_code == 200
    packet = listed.json()
    assert packet["fields"]["count"] == 1
    assert packet["fields"]["items"][0]["id"] == "com.example.text"
    assert packet["fields"]["items"][0]["fields"]["name"] == "Text"

    one = client.get("/api/v1/cards/plugins/com.example.text")
    assert one.status_code == 200
    assert one.json()["type"] == "zen.plugin"
    assert one.json()["fields"]["is_active"] is True

    missing = client.get("/api/v1/cards/plugins/nope")
    assert missing.status_code == 404
    assert missing.json()["fields"]["code"] == "not_found"


def test_execute_plugin_success_and_missing():
    client = _plugin_client()
    ok = client.post(
        "/api/v1/plugins/com.example.text/execute",
        json={"procedure_id": "run", "input": {"n": 1}},
    )
    assert ok.status_code == 200
    assert ok.json()["fields"]["status"] == "done"
    assert ok.json()["fields"]["result"] == {"echo": {"n": 1}}

    missing = client.post(
        "/api/v1/plugins/missing/execute",
        json={"procedure_id": "run", "input": {}},
    )
    assert missing.status_code == 404


def test_inbox_create_and_list(tmp_path: Path):
    service = InboxService(base_path=tmp_path)
    client = TestClient(
        create_app(api_token=None, state=ApiState(api_token=None, inbox_service=service))
    )
    created = client.post(
        "/api/v1/inbox",
        json={"type": "note", "content": "hello greyZ", "metadata": {"src": "test"}},
    )
    assert created.status_code == 201
    packet = created.json()
    assert packet["type"] == "zen.inbox.item"
    assert packet["fields"]["content"] == "hello greyZ"
    assert packet["fields"]["status"] == "new"
    item_id = packet["id"]

    listed = client.get("/api/v1/cards/inbox")
    assert listed.status_code == 200
    items = listed.json()["fields"]["items"]
    assert len(items) == 1
    assert items[0]["id"] == item_id
