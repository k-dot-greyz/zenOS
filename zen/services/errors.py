"""Service-layer errors mapped to zen.error packets."""

from __future__ import annotations

from typing import Any, Mapping, Optional


class ServiceError(Exception):
    """Use-case error with HTTP mapping metadata."""

    status_code = 400
    code = "service_error"

    def __init__(
        self,
        message: str,
        *,
        details: Optional[Mapping[str, Any]] = None,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = dict(details or {})
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(ServiceError):
    """Requested resource does not exist."""

    status_code = 404
    code = "not_found"


class UnavailableError(ServiceError):
    """Upstream dependency is missing or misconfigured."""

    status_code = 503
    code = "unavailable"
