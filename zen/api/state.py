"""Shared FastAPI application state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from zen.api.session import SessionStore


@dataclass
class ApiState:
    """Injectable services and auth config for the HTTP app."""

    api_token: Optional[str] = None
    sessions: SessionStore = field(default_factory=SessionStore)
    agent_service: Any = None
    dex_service: Any = None
    plugin_service: Any = None
    inbox_service: Any = None
    chat_service: Any = None
