"""PR intake gate — `.github/pr-intent.yaml` schema and overlap/stale rules."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

CONTRACT_PATH_PREFIXES = (
    "contracts/",
    "zen/contracts/",
    "dex/registry.yaml",
    ".github/pr-intent.yaml",
    ".github/CODEOWNERS",
)


class PrIntent(BaseModel):
    """Machine-readable PR intake metadata."""

    model_config = ConfigDict(extra="ignore")

    intent: str
    risk: str
    supersedes: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    touches_contracts: bool = False
    expiry_days: int = 14

    @field_validator("risk")
    @classmethod
    def _risk_allowed(cls, value: str) -> str:
        allowed = {"low", "medium", "high"}
        if value not in allowed:
            raise ValueError(f"risk must be one of {sorted(allowed)}")
        return value

    @field_validator("expiry_days")
    @classmethod
    def _expiry_positive(cls, value: int) -> int:
        if value < 1:
            raise ValueError("expiry_days must be >= 1")
        return value

    @field_validator("supersedes", "depends_on", mode="before")
    @classmethod
    def _stringify_refs(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]


def load_pr_intent(path: str | Path) -> PrIntent:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"pr-intent must be a mapping: {path}")
    return PrIntent.model_validate(raw)


def overlap_requires_supersedes(
    ours: Sequence[str],
    theirs: Sequence[str],
    intent: PrIntent,
) -> bool:
    """True when changed-path overlap exists and supersedes was not declared."""
    overlap = {_normalize_path(p) for p in ours} & {_normalize_path(p) for p in theirs}
    if not overlap:
        return False
    return not bool(intent.supersedes)


def changed_paths_touch_contracts(paths: Iterable[str]) -> bool:
    for path in paths:
        normalized = _normalize_path(path)
        if any(
            normalized == prefix.rstrip("/") or normalized.startswith(prefix)
            for prefix in CONTRACT_PATH_PREFIXES
        ):
            return True
    return False


def validate_touches_contracts(paths: Iterable[str], *, declared: bool) -> list[str]:
    """Return error strings when contract paths are touched without the flag."""
    if changed_paths_touch_contracts(paths) and not declared:
        return ["changed paths touch harness contracts; set touches_contracts: true"]
    return []


def is_stale(
    intent: PrIntent,
    *,
    created_at: datetime,
    now: datetime | None = None,
) -> bool:
    current = now or datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    age_days = (current - created_at).days
    return age_days >= intent.expiry_days


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")
