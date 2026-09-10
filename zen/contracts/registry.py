"""Dex capability registry — what / how / proof / supersedes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

ALLOWED_PROFILES = {"ci", "local"}


class RegistryError(ValueError):
    """Raised when a capability entry fails Harness Contract v1 validation."""


class What(BaseModel):
    model_config = ConfigDict(extra="ignore")

    owner: str
    maturity: str
    risk: str
    purpose: str


class How(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entrypoint: str
    env_doctor_profile: str

    def model_post_init(self, __context: Any) -> None:
        if self.env_doctor_profile not in ALLOWED_PROFILES:
            raise RegistryError(f"how.env_doctor_profile must be one of {sorted(ALLOWED_PROFILES)}")


class Proof(BaseModel):
    model_config = ConfigDict(extra="ignore")

    test: str
    artifact: str


class CapabilityEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    what: What
    how: How
    proof: Proof
    supersedes: str | None = None


class CapabilityRegistry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    contract: str
    entries: list[CapabilityEntry] = Field(default_factory=list)


def validate_entry(data: dict[str, Any]) -> CapabilityEntry:
    try:
        return CapabilityEntry.model_validate(data)
    except (ValidationError, RegistryError) as exc:
        raise RegistryError(str(exc)) from exc


def load_registry(path: str | Path) -> CapabilityRegistry:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise RegistryError(f"registry must be a mapping: {path}")
    try:
        registry = CapabilityRegistry.model_validate(raw)
    except ValidationError as exc:
        raise RegistryError(str(exc)) from exc
    if registry.contract != "1.0":
        raise RegistryError(f"unsupported registry contract: {registry.contract!r}")
    return registry


def search_registry(registry: CapabilityRegistry, query: str) -> list[CapabilityEntry]:
    needle = (query or "").strip().lower()
    if not needle:
        return list(registry.entries)
    hits: list[CapabilityEntry] = []
    for entry in registry.entries:
        haystack = " ".join(
            [
                entry.id,
                entry.what.owner,
                entry.what.maturity,
                entry.what.risk,
                entry.what.purpose,
                entry.how.entrypoint,
                entry.proof.test,
                entry.proof.artifact,
                entry.supersedes or "",
            ]
        ).lower()
        if needle in haystack:
            hits.append(entry)
    return hits


def entries_as_dicts(entries: Iterable[CapabilityEntry]) -> list[dict[str, Any]]:
    return [e.model_dump() for e in entries]
