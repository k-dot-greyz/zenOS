"""Packet envelope: handshake schema dump and sysex-style deltas."""

from zen.api.envelope import (
    CARD_TYPE_FIELDS,
    PACKET_KINDS,
    SCHEMA_ID,
    SCHEMA_VERSION,
    DeltaEncoder,
    compact_fields,
    handshake_schema,
    make_card,
    make_collection,
    make_delta,
    make_done,
    make_error,
)


def test_handshake_schema_includes_packet_kinds_and_card_types():
    schema = handshake_schema()
    assert schema["schema_id"] == SCHEMA_ID
    assert schema["v"] == SCHEMA_VERSION
    assert set(schema["packet_kinds"]) == set(PACKET_KINDS)
    for card_type, fields in CARD_TYPE_FIELDS.items():
        assert card_type in schema["card_types"]
        assert schema["card_types"][card_type]["fields"] == list(fields)
    for cap in ("agents", "dex", "plugins", "inbox", "chat"):
        assert cap in schema["capabilities"]


def test_make_card_omits_none_fields_but_keeps_wire_keys():
    packet = make_card(
        "zen.agent",
        "critic",
        {"name": "critic", "description": "reviews prompts", "author": None, "version": "1.0.0"},
        sid="sess-1",
        seq=3,
    )
    wire = packet.to_wire()
    assert wire["v"] == SCHEMA_VERSION
    assert wire["sid"] == "sess-1"
    assert wire["seq"] == 3
    assert wire["kind"] == "card"
    assert wire["type"] == "zen.agent"
    assert wire["id"] == "critic"
    assert wire["fields"] == {
        "name": "critic",
        "description": "reviews prompts",
        "version": "1.0.0",
    }
    assert "author" not in wire["fields"]


def test_delta_encoder_omits_unchanged_and_none_values():
    encoder = DeltaEncoder()
    first = encoder.delta({"text": "he", "status": "running", "error": None})
    assert first == {"text": "he", "status": "running"}
    second = encoder.delta({"text": "hello", "status": "running"})
    assert second == {"text": "hello"}
    third = encoder.delta({"text": "hello", "status": "running"})
    assert third == {}
    fourth = encoder.delta({"text": "hello", "status": "done"})
    assert fourth == {"status": "done"}


def test_make_delta_and_done_packets():
    delta = make_delta("sid-a", 4, {"text": "chunk"}, card_type="zen.chat", card_id="chat-1")
    wire = delta.to_wire()
    assert wire["kind"] == "delta"
    assert wire["type"] == "zen.chat"
    assert wire["id"] == "chat-1"
    assert wire["fields"] == {"text": "chunk"}

    done = make_done("sid-a", 5, card_id="chat-1")
    done_wire = done.to_wire()
    assert done_wire["kind"] == "done"
    assert done_wire["id"] == "chat-1"
    assert done_wire["fields"] == {}


def test_make_error_is_zen_error_card():
    packet = make_error("not_found", "Agent not found", details={"id": "nope"}, sid="s", seq=1)
    wire = packet.to_wire()
    assert wire["kind"] == "error"
    assert wire["type"] == "zen.error"
    assert wire["fields"]["code"] == "not_found"
    assert wire["fields"]["message"] == "Agent not found"
    assert wire["fields"]["details"] == {"id": "nope"}


def test_make_collection_wraps_item_cards():
    items = [
        make_card("zen.agent", "a", {"name": "a"}),
        make_card("zen.agent", "b", {"name": "b"}),
    ]
    collection = make_collection("zen.agent", items, sid="s", seq=2)
    wire = collection.to_wire()
    assert wire["type"] == "zen.collection"
    assert wire["id"] == "zen.agent"
    assert wire["fields"]["count"] == 2
    assert wire["fields"]["item_type"] == "zen.agent"
    assert wire["fields"]["items"] == [
        {"id": "a", "fields": {"name": "a"}},
        {"id": "b", "fields": {"name": "b"}},
    ]


def test_compact_fields_skips_none_keeps_false_and_zero():
    assert compact_fields({"a": None, "b": 0, "c": False, "d": ""}) == {
        "b": 0,
        "c": False,
        "d": "",
    }
