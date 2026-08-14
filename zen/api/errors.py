"""HTTP packet errors mapped to zen.error cards."""

from __future__ import annotations

from typing import Any, Mapping, Optional


class PacketError(Exception):
    """API error that serializes as a zen.error packet."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        details: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = dict(details or {})
