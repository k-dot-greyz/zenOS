"""DexService model/procedure card endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from zen.api.app import create_app
from zen.api.state import ApiState
from zen.dex.catalog import DexCatalog
from zen.services.dex import DexService

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "dex"


def _service() -> DexService:
    catalog = DexCatalog(base_path=FIXTURES)
    return DexService(catalog=catalog)


def _client(service: DexService | None = None) -> TestClient:
    svc = service or _service()
    return TestClient(create_app(api_token=None, state=ApiState(api_token=None, dex_service=svc)))


def test_list_models_and_filter_by_tier():
    client = _client()
    response = client.get("/api/v1/cards/models")
    assert response.status_code == 200
    packet = response.json()
    assert packet["type"] == "zen.collection"
    assert packet["fields"]["item_type"] == "zen.model"
    assert packet["fields"]["count"] == 2
    ids = {item["id"] for item in packet["fields"]["items"]}
    assert ids == {"test/fast-model", "test/legend"}

    filtered = client.get("/api/v1/cards/models", params={"tier": "legendary"})
    assert filtered.status_code == 200
    items = filtered.json()["fields"]["items"]
    assert len(items) == 1
    assert items[0]["id"] == "test/legend"
    assert items[0]["fields"]["tier"] == "legendary"


def test_get_model_card_and_missing():
    client = _client()
    response = client.get("/api/v1/cards/models/test/fast-model")
    assert response.status_code == 200
    packet = response.json()
    assert packet["type"] == "zen.model"
    assert packet["id"] == "test/fast-model"
    assert packet["fields"]["provider"] == "test"

    missing = client.get("/api/v1/cards/models/nope")
    assert missing.status_code == 404
    assert missing.json()["fields"]["code"] == "not_found"


def test_list_procedures_filter_and_stats():
    client = _client()
    response = client.get("/api/v1/cards/procedures", params={"type": "analytical"})
    assert response.status_code == 200
    items = response.json()["fields"]["items"]
    assert len(items) == 1
    assert items[0]["id"] == "zen.analyze"

    one = client.get("/api/v1/cards/procedures/zen.chat")
    assert one.status_code == 200
    assert one.json()["fields"]["name"] == "Basic Chat"

    stats = client.get("/api/v1/dex/stats")
    assert stats.status_code == 200
    fields = stats.json()["fields"]
    assert fields["total_models"] == 2
    assert fields["total_procedures"] == 2
    assert fields["model_tiers"]["legendary"] == 1


class _FakeSyncer:
    def __init__(self) -> None:
        self.called = False
        self.cache_file = Path("/tmp/zen-dex-cache-does-not-exist.json")

    async def sync_dex(self) -> None:
        self.called = True


def test_dex_sync_uses_injected_syncer():
    syncer = _FakeSyncer()
    service = DexService(catalog=DexCatalog(base_path=FIXTURES), syncer=syncer)
    client = _client(service)
    response = client.post("/api/v1/dex/sync")
    assert response.status_code == 200
    assert syncer.called
    assert response.json()["type"] == "zen.dex.stats"
    assert response.json()["fields"]["total_models"] == 2
