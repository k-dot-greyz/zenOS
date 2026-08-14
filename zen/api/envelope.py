"""JSON card packet envelope: handshake schema dump, then delta-only fields."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1
SCHEMA_ID = "zen.packet.v1"

PACKET_KINDS = ("card", "delta", "done", "error")

CARD_TYPE_FIELDS: Dict[str, tuple[str, ...]] = {
    "zen.agent": ("name", "description", "type", "version", "author", "tags"),
    "zen.model": (
        "name",
        "provider",
        "type",
        "tier",
        "stats",
        "feats",
        "best_for",
        "context_window",
        "cost_per_1k",
    ),
    "zen.procedure": (
        "name",
        "type",
        "tier",
        "stats",
        "requirements",
        "discovered_by",
        "usage_count",
    ),
    "zen.plugin": (
        "name",
        "version",
        "author",
        "description",
        "category",
        "capabilities",
        "is_active",
        "usage_count",
    ),
    "zen.inbox.item": ("type", "content", "metadata", "status", "created_at", "updated_at"),
    "zen.error": ("code", "message", "details"),
    "zen.meta": ("version", "schema_id", "capabilities"),
    "zen.session": ("schema_id", "v", "packet_kinds", "card_types", "capabilities"),
    "zen.collection": ("item_type", "count", "items"),
    "zen.dex.stats": (
        "total_models",
        "total_procedures",
        "model_tiers",
        "procedure_types",
        "achievements_available",
        "combos_discovered",
    ),
    "zen.chat": ("text", "status", "model", "error"),
    "zen.execute": ("text", "status", "result", "error"),
}

CAPABILITIES = ("agents", "dex", "plugins", "inbox", "chat")

PacketKind = Literal["card", "delta", "done", "error"]


def compact_fields(fields: Mapping[str, Any]) -> Dict[str, Any]:
    """Drop None values; keep 0, False, and empty strings."""
    return {key: value for key, value in fields.items() if value is not None}


def handshake_schema() -> Dict[str, Any]:
    """Full packet schema dump (sysex-style) advertised at session start."""
    return {
        "schema_id": SCHEMA_ID,
        "v": SCHEMA_VERSION,
        "packet_kinds": list(PACKET_KINDS),
        "card_types": {
            card_type: {"fields": list(field_names)}
            for card_type, field_names in CARD_TYPE_FIELDS.items()
        },
        "capabilities": list(CAPABILITIES),
    }


class Packet(BaseModel):
    """One envelope packet on the wire."""

    model_config = ConfigDict(extra="forbid")

    v: int = SCHEMA_VERSION
    sid: Optional[str] = None
    seq: int = 0
    kind: PacketKind
    type: Optional[str] = None
    id: Optional[str] = None
    fields: Dict[str, Any] = Field(default_factory=dict)

    def to_wire(self) -> Dict[str, Any]:
        """Serialize with a stable top-level schema and compacted fields."""
        return {
            "v": self.v,
            "sid": self.sid,
            "seq": self.seq,
            "kind": self.kind,
            "type": self.type,
            "id": self.id,
            "fields": compact_fields(self.fields),
        }


class DeltaEncoder:
    """Emit only fields that changed since the last snapshot."""

    def __init__(self) -> None:
        self._last: Dict[str, Any] = {}

    def reset(self) -> None:
        """Clear the last-sent snapshot."""
        self._last = {}

    def delta(self, fields: Mapping[str, Any]) -> Dict[str, Any]:
        """Return keys whose values are new or changed; skip None and unchanged."""
        out: Dict[str, Any] = {}
        for key, value in fields.items():
            if value is None:
                continue
            if key in self._last and self._last[key] == value:
                continue
            out[key] = value
            self._last[key] = value
        return out


def make_card(
    card_type: str,
    card_id: Optional[str],
    fields: Mapping[str, Any],
    *,
    sid: Optional[str] = None,
    seq: int = 0,
) -> Packet:
    """Build a full card packet with None fields omitted."""
    return Packet(
        sid=sid,
        seq=seq,
        kind="card",
        type=card_type,
        id=card_id,
        fields=compact_fields(fields),
    )


def make_delta(
    sid: Optional[str],
    seq: int,
    fields: Mapping[str, Any],
    *,
    card_type: Optional[str] = None,
    card_id: Optional[str] = None,
) -> Packet:
    """Build a delta packet; caller should already have omitted unchanged keys."""
    return Packet(
        sid=sid,
        seq=seq,
        kind="delta",
        type=card_type,
        id=card_id,
        fields=compact_fields(fields),
    )


def make_done(
    sid: Optional[str],
    seq: int,
    *,
    card_id: Optional[str] = None,
    card_type: Optional[str] = None,
) -> Packet:
    """Build a terminal done packet for a stream."""
    return Packet(sid=sid, seq=seq, kind="done", type=card_type, id=card_id, fields={})


def make_error(
    code: str,
    message: str,
    *,
    details: Optional[Mapping[str, Any]] = None,
    sid: Optional[str] = None,
    seq: int = 0,
) -> Packet:
    """Build a zen.error packet."""
    return Packet(
        sid=sid,
        seq=seq,
        kind="error",
        type="zen.error",
        id=None,
        fields={"code": code, "message": message, "details": dict(details or {})},
    )


def make_collection(
    item_type: str,
    items: Iterable[Packet],
    *,
    sid: Optional[str] = None,
    seq: int = 0,
) -> Packet:
    """Wrap item cards in a zen.collection packet."""
    item_list: List[Dict[str, Any]] = []
    for packet in items:
        item_list.append({"id": packet.id, "fields": compact_fields(packet.fields)})
    return Packet(
        sid=sid,
        seq=seq,
        kind="card",
        type="zen.collection",
        id=item_type,
        fields={"item_type": item_type, "count": len(item_list), "items": item_list},
    )
