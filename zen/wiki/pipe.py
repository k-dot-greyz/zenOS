"""HTTP client for Visual Wiki open-piping (/api/pipe)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


def default_base_url() -> str:
    return os.environ.get("ZEN_VISUAL_WIKI_URL", "http://localhost:3000").rstrip("/")


def fetch_handshake(base_url: Optional[str] = None) -> Dict[str, Any]:
    """GET /api/pipe — schema handshake and resource index."""
    base = (base_url or default_base_url()).rstrip("/")
    with urllib.request.urlopen(f"{base}/api/pipe", timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def pipe_url(
    url: str,
    *,
    base_url: Optional[str] = None,
    resource_type: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """POST /api/pipe — ingest a URL or raw resource into the garden."""
    base = (base_url or default_base_url()).rstrip("/")
    body: Dict[str, Any] = {"url": url}
    if resource_type:
        body["type"] = resource_type
    if payload:
        body["payload"] = payload

    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        f"{base}/api/pipe",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Pipe failed ({exc.code}): {detail}") from exc
