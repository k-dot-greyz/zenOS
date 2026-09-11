"""In-memory API session store for handshake sequence numbers."""

from __future__ import annotations

from time import monotonic
from typing import Dict, Optional, Tuple
from uuid import uuid4

DEFAULT_TTL_SECONDS = 3600.0
DEFAULT_MAX_SESSIONS = 1024


class SessionStore:
    """Track handshake sessions and monotonically increasing packet seq.

    Sessions expire after ``ttl_seconds`` of inactivity and the store drops
    the oldest entries when ``max_sessions`` is exceeded.
    """

    def __init__(
        self,
        *,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        max_sessions: int = DEFAULT_MAX_SESSIONS,
    ) -> None:
        self._ttl = ttl_seconds
        self._max = max_sessions
        self._sessions: Dict[str, Tuple[int, float]] = {}

    def _purge(self, *, now: Optional[float] = None, room_for: int = 0) -> None:
        stamp = monotonic() if now is None else now
        expired = [
            sid for sid, (_, last_seen) in self._sessions.items() if stamp - last_seen > self._ttl
        ]
        for sid in expired:
            del self._sessions[sid]
        overflow = len(self._sessions) + room_for - self._max
        if overflow <= 0:
            return
        oldest = sorted(self._sessions.items(), key=lambda item: item[1][1])[:overflow]
        for sid, _ in oldest:
            del self._sessions[sid]

    def create(self) -> str:
        """Create a session and return its id."""
        self._purge(room_for=1)
        sid = str(uuid4())
        self._sessions[sid] = (0, monotonic())
        return sid

    def exists(self, sid: str) -> bool:
        """Return True if the session was created via handshake and is live."""
        self._purge()
        return sid in self._sessions

    def next_seq(self, sid: Optional[str]) -> int:
        """Increment and return seq for a known session; 0 if anonymous."""
        if not sid:
            return 0
        self._purge()
        entry = self._sessions.get(sid)
        if entry is None:
            return 0
        seq = entry[0] + 1
        self._sessions[sid] = (seq, monotonic())
        return seq
