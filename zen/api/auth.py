"""Bearer token auth and bind-address policy."""

from __future__ import annotations

from typing import Optional

from fastapi import Header, Request

from zen.api.errors import PacketError

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1", "0:0:0:0:0:0:0:1"})


def is_loopback_host(host: str) -> bool:
    """Return True if host is a loopback address or name."""
    return host.strip().lower() in LOOPBACK_HOSTS


def require_token_for_bind(host: str, token: Optional[str]) -> None:
    """Refuse non-loopback binds unless an API token is configured."""
    if not is_loopback_host(host) and not token:
        raise ValueError(
            "ZEN_API_TOKEN is required when binding to a non-loopback address"
        )


async def require_api_token(
    request: Request,
    authorization: Optional[str] = Header(default=None),
) -> None:
    """Require Bearer token when the app was created with an API token."""
    expected = request.app.state.zen.api_token
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise PacketError(401, "unauthorized", "Bearer token required")
    provided = authorization[7:].strip()
    if provided != expected:
        raise PacketError(401, "unauthorized", "Invalid token")
