"""In-memory API session store for handshake sequence numbers."""

from __future__ import annotations

from typing import Dict, Optional
from uuid import uuid4


class SessionStore:
    """Track handshake sessions and monotonically increasing packet seq."""

    def __init__(self) -> None:
        self._sessions: Dict[str, int] = {}

    def create(self) -> str:
        """Create a session and return its id."""
        sid = str(uuid4())
        self._sessions[sid] = 0
        return sid

    def exists(self, sid: str) -> bool:
        """Return True if the session was created via handshake."""
        return sid in self._sessions

    def next_seq(self, sid: Optional[str]) -> int:
        """Increment and return seq for a known session; 0 if anonymous."""
        if not sid or sid not in self._sessions:
            return 0
        self._sessions[sid] += 1
        return self._sessions[sid]
