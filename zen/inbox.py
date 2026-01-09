#!/usr/bin/env python3
"""zenOS Inbox System - Process incoming items
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import click


class InboxManager:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.inbox_path = self.base_path / "inbox"
        self.incoming_path = self.inbox_path / "incoming"
        self.processing_path = self.inbox_path / "processing"
        self.processed_path = self.inbox_path / "processed"

    def add_item(self, item_type: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a new item to the inbox"""
        timestamp = datetime.now().isoformat()
        item_id = f"{item_type}_{timestamp.replace(':', '-')}"

        item = {
            "id": item_id,
            "type": item_type,
            "content": content,
            "metadata": metadata or {},
            "status": "new",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Save to incoming
        item_file = self.incoming_path / f"{item_id}.json"
        with open(item_file, "w") as f:
            json.dump(item, f, indent=2)

        return item_id

    def list_items(self, status: str = None) -> list:
        """List items in the inbox"""
        items = []

        for path in [self.incoming_path, self.processing_path, self.processed_path]:
            if not path.exists():
                continue

            for item_file in path.glob("*.json"):
                try:
                    with open(item_file, "r") as f:
                        item = json.load(f)
                        if not status or item.get("status") == status:
                            items.append(item)
                except Exception as e:
                    print(f"Error reading {item_file}: {e}")

        return sorted(items, key=lambda x: x["created_at"], reverse=True)

    def move_item(self, item_id: str, from_status: str, to_status: str) -> bool:
        """Move an item between statuses"""
        status_paths = {
            "new": self.incoming_path,
            "processing": self.processing_path,
            "processed": self.processed_path,
        }

        if from_status not in status_paths or to_status not in status_paths:
            return False

        source_path = status_paths[from_status] / f"{item_id}.json"
        target_path = status_paths[to_status] / f"{item_id}.json"

        if not source_path.exists():
            return False

        # Move file
        source_path.rename(target_path)

        # Update status in file
        with open(target_path, "r") as f:
            item = json.load(f)

        item["status"] = to_status
        item["updated_at"] = datetime.now().isoformat()

        with open(target_path, "w") as f:
            json.dump(item, f, indent=2)

        return True


@click.group()
@click.alias("inbox")
def receive():
    """ZenOS Receive System - Process incoming items"""
    pass


@receive.command()
@click.argument("item_type")
@click.argument("content")
@click.option("--metadata", help="JSON metadata for the item")
def add(item_type: str, content: str, metadata: str = None):
    """Add a new item to the inbox"""
    manager = InboxManager()

    metadata_dict = {}
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON metadata")
            return

    item_id = manager.add_item(item_type, content, metadata_dict)
    click.echo(f"Added {item_type} item: {item_id}")


@receive.command()
@click.option("--status", help="Filter by status (new, processing, processed)")
def list(status: str = None):
    """List items in the inbox"""
    manager = InboxManager()
    items = manager.list_items(status)

    if not items:
        click.echo("No items found")
        return

    for item in items:
        status_emoji = {"new": "🆕", "processing": "⚙️", "processed": "✅"}.get(item["status"], "❓")

        click.echo(f"{status_emoji} {item['id']} - {item['type']} - {item['content'][:50]}...")


@receive.command()
@click.argument("item_id")
@click.argument("to_status")
def move(item_id: str, to_status: str):
    """Move an item to a different status"""
    manager = InboxManager()

    # Find current status
    current_status = None
    for status in ["new", "processing", "processed"]:
        status_path = getattr(manager, f"{status}_path")
        if (status_path / f"{item_id}.json").exists():
            current_status = status
            break

    if not current_status:
        click.echo(f"Item {item_id} not found")
        return

    if manager.move_item(item_id, current_status, to_status):
        click.echo(f"Moved {item_id} from {current_status} to {to_status}")
    else:
        click.echo(f"Failed to move {item_id}")


if __name__ == "__main__":
    receive()
