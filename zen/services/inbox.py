"""Inbox capture use cases."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from zen.inbox import InboxManager


class InboxService:
    """Create and list inbox items without Click I/O."""

    def __init__(
        self, manager: Optional[InboxManager] = None, base_path: Optional[Any] = None
    ) -> None:
        if manager is not None:
            self.manager = manager
        else:
            self.manager = InboxManager(str(base_path) if base_path is not None else ".")

    def list_items(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List inbox items, optionally filtered by status."""
        return self.manager.list_items(status)

    def add_item(
        self,
        item_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Capture an inbox item and return the stored record."""
        item_id = self.manager.add_item(item_type, content, metadata)
        for item in self.manager.list_items():
            if item.get("id") == item_id:
                return item
        return {
            "id": item_id,
            "type": item_type,
            "content": content,
            "metadata": metadata or {},
            "status": "new",
        }

    def item_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize an inbox item to card fields."""
        return {
            "type": item.get("type"),
            "content": item.get("content"),
            "metadata": item.get("metadata") or {},
            "status": item.get("status"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
        }
