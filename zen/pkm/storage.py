"""Storage and retrieval system for PKM module."""

import gzip
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import PKMConfig
from .models import Conversation, KnowledgeEntry, MessageRole


class PKMStorage:
    """Storage system for PKM data."""

    def __init__(self, config: PKMConfig):
        """Initialize the PKMStorage with the given configuration and ensure required storage directories exist.

        Parameters
        ----------
            config (PKMConfig): Configuration containing `conversations_dir`, `knowledge_base_dir`, and `exports_dir`; those directories will be created if they do not already exist.

        """
        self.config = config
        self.conversations_dir = config.conversations_dir
        self.knowledge_base_dir = config.knowledge_base_dir
        self.exports_dir = config.exports_dir

        # Ensure directories exist
        for directory in [self.conversations_dir, self.knowledge_base_dir, self.exports_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def save_conversation(self, conversation: Conversation) -> bool:
        """Persist the given Conversation to disk using the configured storage format.

        Writes the conversation to JSON and/or Markdown files under the configured conversations directory,
        and updates the conversation's file_path and file_size when a JSON file is written.

        Parameters
        ----------
            conversation (Conversation): Conversation model to persist; its `to_dict()` representation is written.

        Returns
        -------
            bool: `True` if the conversation was successfully written, `False` if an error occurred.

        """
        try:
            # Save as JSON
            if self.config.storage_format in ["json", "both"]:
                json_path = self.conversations_dir / f"{conversation.id}.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(conversation.to_dict(), f, indent=2, ensure_ascii=False)
                conversation.file_path = str(json_path)
                conversation.file_size = json_path.stat().st_size

            # Save as Markdown
            if self.config.storage_format in ["markdown", "both"]:
                md_path = self.conversations_dir / f"{conversation.id}.md"
                markdown_content = self._conversation_to_markdown(conversation)
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

            return True

        except Exception as e:
            print(f"Error saving conversation {conversation.id}: {e}")
            return False

    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Load a Conversation object with the given ID from storage.

        Returns:
            Conversation: The loaded Conversation if the corresponding JSON file exists and is parsed successfully, `None` if the file does not exist or an error occurs while reading or parsing.

        """
        json_path = self.conversations_dir / f"{conversation_id}.json"

        if not json_path.exists():
            return None

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Conversation.from_dict(data)
        except Exception as e:
            print(f"Error loading conversation {conversation_id}: {e}")
            return None

    def list_conversations(self, limit: Optional[int] = None) -> List[Conversation]:
        """Retrieve stored conversations sorted by most recently updated.

        Parameters
        ----------
                limit (int | None): Maximum number of conversations to return. If omitted or None, all conversations are returned.

        Returns
        -------
                conversations (List[Conversation]): Conversations sorted by `updated_at` in descending order, truncated to `limit` when provided.

        """
        conversations = []

        for json_file in self.conversations_dir.glob("*.json"):
            conversation = self.load_conversation(json_file.stem)
            if conversation:
                conversations.append(conversation)

        # Sort by updated_at descending
        conversations.sort(key=lambda x: x.updated_at, reverse=True)

        if limit:
            conversations = conversations[:limit]

        return conversations

    def search_conversations(self, query: str, limit: Optional[int] = None) -> List[Conversation]:
        """Search conversations for a case-insensitive query across title, message contents, and summary.

        Parameters
        ----------
                query (str): The substring to match (case-insensitive) against conversation title, any message content, or the conversation summary.
                limit (Optional[int]): Maximum number of matching conversations to return. If omitted or None, returns all matches.

        Returns
        -------
                matches (List[Conversation]): Conversations that contain the query in title, any message, or summary. Results preserve the order returned by list_conversations and are truncated to `limit` when provided.

        """
        results = []
        query_lower = query.lower()

        for conversation in self.list_conversations():
            # Search in title
            if query_lower in conversation.title.lower():
                results.append(conversation)
                continue

            # Search in messages
            for message in conversation.messages:
                if query_lower in message.content.lower():
                    results.append(conversation)
                    break

            # Search in summary
            if conversation.summary and query_lower in conversation.summary.lower():
                results.append(conversation)
                continue

        if limit:
            results = results[:limit]

        return results

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation files for the given conversation id from storage.

        Removes both the JSON and Markdown files named {conversation_id}.json and {conversation_id}.md in the conversations directory if they exist.

        Parameters
        ----------
            conversation_id (str): Identifier of the conversation to delete.

        Returns
        -------
            bool: True if deletion succeeded (or files were already absent), False if an error occurred.

        """
        try:
            # Delete JSON file
            json_path = self.conversations_dir / f"{conversation_id}.json"
            if json_path.exists():
                json_path.unlink()

            # Delete Markdown file
            md_path = self.conversations_dir / f"{conversation_id}.md"
            if md_path.exists():
                md_path.unlink()

            return True

        except Exception as e:
            print(f"Error deleting conversation {conversation_id}: {e}")
            return False

    def save_knowledge_entry(self, entry: KnowledgeEntry) -> bool:
        """Persist a KnowledgeEntry to the configured knowledge base directory as a JSON file.

        Writes the entry to a file named "{entry.id}.json" in the storage knowledge base directory. Overwrites any existing file with the same id.

        Parameters
        ----------
            entry (KnowledgeEntry): The knowledge entry to persist.

        Returns
        -------
            bool: `true` if the entry was written successfully, `false` otherwise.

        """
        try:
            json_path = self.knowledge_base_dir / f"{entry.id}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(entry.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving knowledge entry {entry.id}: {e}")
            return False

    def load_knowledge_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Load a knowledge entry from disk by its identifier.

        Parameters
        ----------
            entry_id (str): Identifier of the knowledge entry (filename without the .json extension).

        Returns
        -------
            Optional[KnowledgeEntry]: The loaded KnowledgeEntry instance if the file exists and parses successfully, `None` if the file is missing or an error occurs while reading/parsing.

        """
        json_path = self.knowledge_base_dir / f"{entry_id}.json"

        if not json_path.exists():
            return None

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return KnowledgeEntry(**data)
        except Exception as e:
            print(f"Error loading knowledge entry {entry_id}: {e}")
            return None

    def list_knowledge_entries(self, limit: Optional[int] = None) -> List[KnowledgeEntry]:
        """Return stored knowledge entries sorted by `updated_at` in descending order.

        Parameters
        ----------
            limit (Optional[int]): Maximum number of entries to return; if omitted or None, return all entries.

        Returns
        -------
            List[KnowledgeEntry]: List of knowledge entries sorted from newest to oldest by `updated_at`.

        """
        entries = []

        for json_file in self.knowledge_base_dir.glob("*.json"):
            entry = self.load_knowledge_entry(json_file.stem)
            if entry:
                entries.append(entry)

        # Sort by updated_at descending
        entries.sort(key=lambda x: x.updated_at, reverse=True)

        if limit:
            entries = entries[:limit]

        return entries

    def search_knowledge_entries(
        self, query: str, limit: Optional[int] = None
    ) -> List[KnowledgeEntry]:
        """Search knowledge entries for a case-insensitive match in title, content, or tags.

        Parameters
        ----------
            query (str): Substring to search for within entry title, content, and tags.
            limit (Optional[int]): Maximum number of results to return; if omitted, all matches are returned.

        Returns
        -------
            List[KnowledgeEntry]: Matching knowledge entries, up to `limit` if provided.

        """
        results = []
        query_lower = query.lower()

        for entry in self.list_knowledge_entries():
            # Search in title
            if query_lower in entry.title.lower():
                results.append(entry)
                continue

            # Search in content
            if query_lower in entry.content.lower():
                results.append(entry)
                continue

            # Search in tags
            for tag in entry.tags:
                if query_lower in tag.lower():
                    results.append(entry)
                    break

        if limit:
            results = results[:limit]

        return results

    def export_conversations(self, format: str = "json", limit: Optional[int] = None) -> Path:
        """Export stored conversations to a timestamped file in the configured exports directory.

        Writes conversations retrieved via list_conversations(limit) to a file named with the current timestamp. Supports JSON and Markdown output: `"json"` writes a single JSON array of conversation dicts; `"markdown"` writes each conversation as Markdown separated by a delimiter.

        Parameters
        ----------
            format (str): Export format, either `"json"` or `"markdown"`.
            limit (Optional[int]): Maximum number of conversations to include; if None, includes all.

        Returns
        -------
            Path: Path to the created export file.

        Raises
        ------
            ValueError: If an unsupported export format is provided.

        """
        conversations = self.list_conversations(limit)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            export_path = self.exports_dir / f"conversations_{timestamp}.json"
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(
                    [conv.to_dict() for conv in conversations], f, indent=2, ensure_ascii=False
                )

        elif format == "markdown":
            export_path = self.exports_dir / f"conversations_{timestamp}.md"
            with open(export_path, "w", encoding="utf-8") as f:
                for conversation in conversations:
                    f.write(self._conversation_to_markdown(conversation))
                    f.write("\n\n---\n\n")

        else:
            raise ValueError(f"Unsupported export format: {format}")

        return export_path

    def export_knowledge_base(self, format: str = "json", limit: Optional[int] = None) -> Path:
        """Export the knowledge base to a timestamped file in the configured exports directory.

        Parameters
        ----------
            format (str): Export format, either "json" for a JSON array of entry objects or "markdown" for a human-readable Markdown document. Unsupported values raise ValueError.
            limit (Optional[int]): Maximum number of knowledge entries to include; if None all entries are exported.

        Returns
        -------
            Path: Path to the created export file.

        Raises
        ------
            ValueError: If `format` is not "json" or "markdown".

        """
        entries = self.list_knowledge_entries(limit)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            export_path = self.exports_dir / f"knowledge_base_{timestamp}.json"
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump([entry.to_dict() for entry in entries], f, indent=2, ensure_ascii=False)

        elif format == "markdown":
            export_path = self.exports_dir / f"knowledge_base_{timestamp}.md"
            with open(export_path, "w", encoding="utf-8") as f:
                for entry in entries:
                    f.write(f"# {entry.title}\n\n")
                    f.write(f"**Type:** {entry.entry_type}\n")
                    f.write(f"**Confidence:** {entry.confidence}\n")
                    f.write(f"**Tags:** {', '.join(entry.tags)}\n\n")
                    f.write(entry.content)
                    f.write("\n\n---\n\n")

        else:
            raise ValueError(f"Unsupported export format: {format}")

        return export_path

    def cleanup_old_data(self, days: int = 30) -> int:
        """Remove or compress conversation JSON files whose modification time is older than the specified cutoff.

        Parameters
        ----------
            days (int): Age cutoff in days; files with modification time strictly older than (now - days) are processed.

        Returns
        -------
            cleaned_count (int): Number of conversation files that were deleted or compressed.

        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0

        # Clean up old conversations
        for json_file in self.conversations_dir.glob("*.json"):
            if json_file.stat().st_mtime < cutoff_date.timestamp():
                # Compress if enabled
                if self.config.compress_old_conversations:
                    compressed_path = json_file.with_suffix(".json.gz")
                    with open(json_file, "rb") as f_in:
                        with gzip.open(compressed_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    json_file.unlink()
                else:
                    json_file.unlink()
                cleaned_count += 1

        return cleaned_count

    def _conversation_to_markdown(self, conversation: Conversation) -> str:
        """Render a Conversation as a Markdown-formatted string.

        Includes a header with title, id, created and updated timestamps, URL, and status.
        Formats each message with an emoji indicating the role, a role label, and a timestamp,
        followed by the message content. If present, appends "Summary", "Keywords", and
        "Tags" sections.

        Parameters
        ----------
            conversation (Conversation): The conversation to convert.

        Returns
        -------
            markdown (str): The conversation serialized as a Markdown document.

        """
        lines = [
            f"# {conversation.title}",
            "",
            f"**ID:** {conversation.id}",
            f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Updated:** {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**URL:** {conversation.url or 'N/A'}",
            f"**Status:** {conversation.status.value}",
            "",
            "---",
            "",
        ]

        for i, message in enumerate(conversation.messages, 1):
            role_emoji = "👤" if message.role == MessageRole.USER else "🤖"
            timestamp = message.timestamp.strftime("%H:%M:%S") if message.timestamp else "Unknown"

            lines.extend(
                [
                    f"## {role_emoji} {message.role.value.title()} ({timestamp})",
                    "",
                    message.content,
                    "",
                ]
            )

        if conversation.summary:
            lines.extend(
                [
                    "---",
                    "",
                    "## Summary",
                    "",
                    conversation.summary,
                    "",
                ]
            )

        if conversation.keywords:
            lines.extend(
                [
                    "## Keywords",
                    "",
                    ", ".join(conversation.keywords),
                    "",
                ]
            )

        if conversation.tags:
            lines.extend(
                [
                    "## Tags",
                    "",
                    ", ".join(conversation.tags),
                    "",
                ]
            )

        return "\n".join(lines)

    def get_statistics(self) -> Dict[str, Any]:
        """Compute statistics about stored conversations and storage usage.

        The function aggregates conversations from storage and computes totals and breakdowns.

        Returns:
            stats (Dict[str, Any]): A dictionary containing:
                - "total_conversations" (int): Number of conversations indexed.
                - "total_messages" (int): Sum of messages across all conversations.
                - "total_size_bytes" (int): Sum of `file_size` for all conversations (bytes; treats missing sizes as 0).
                - "total_size_mb" (float): `total_size_bytes` converted to megabytes, rounded to two decimals.
                - "status_breakdown" (Dict[str, int]): Mapping of conversation status values to their counts.
                - "storage_path" (str): Path to the conversations storage directory as a string.

        """
        conversations = self.list_conversations()

        total_messages = sum(len(conv.messages) for conv in conversations)
        total_size = sum(conv.file_size or 0 for conv in conversations)

        status_counts = {}
        for conv in conversations:
            status = conv.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_conversations": len(conversations),
            "total_messages": total_messages,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "status_breakdown": status_counts,
            "storage_path": str(self.config.conversations_dir),
        }
