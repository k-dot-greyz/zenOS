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

REQUIRED_FIELDS = (
    "intent",
    "risk",
    "supersedes",
    "depends_on",
    "touches_contracts",
    "expiry_days",
)


class PrIntent(BaseModel):
    """Machine-readable PR intake metadata."""

    model_config = ConfigDict(extra="ignore")

    intent: str = Field(min_length=1)
    risk: str
    supersedes: list[str]
    depends_on: list[str]
    touches_contracts: bool
    expiry_days: int = 14

    @field_validator("intent")
    @classmethod
    def _intent_nonempty(cls, value: str) -> str:
        if not (value or "").strip():
            raise ValueError("intent must be non-empty")
        return value

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
        if not isinstance(value, list):
            raise ValueError("supersedes and depends_on must be arrays")
        return [str(item) for item in value]


def load_pr_intent(path: str | Path) -> PrIntent:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"pr-intent must be a mapping: {path}")
    missing = [field for field in REQUIRED_FIELDS if field not in raw]
    if missing:
        raise ValueError(f"pr-intent missing required fields: {missing}")
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


def overlap_violations(
    ours: Sequence[str],
    others: Sequence[tuple[str, Sequence[str]]],
    intent: PrIntent,
) -> list[str]:
    """Error strings when overlapping *contract* paths lack supersedes.

    README/pyproject drive-bys across unrelated open PRs are not Track 3
    replacements. Contract surfaces (see CONTRACT_PATH_PREFIXES) still fail
    closed.
    """
    errors: list[str] = []
    superseded = {str(item) for item in intent.supersedes}
    our_contract = {_normalize_path(p) for p in ours if changed_paths_touch_contracts([p])}
    if not our_contract:
        return []
    for number, theirs in others:
        their_contract = {_normalize_path(p) for p in theirs if changed_paths_touch_contracts([p])}
        overlap = our_contract & their_contract
        if overlap and str(number) not in superseded:
            sample = ", ".join(sorted(overlap)[:5])
            errors.append(f"changed paths overlap open PR #{number} ({sample}); declare supersedes")
    return errors


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
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized
