"""Data models for PKM module."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ConversationStatus(Enum):
    """Status of a conversation extraction."""

    PENDING = "pending"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class MessageRole(Enum):
    """Role of a message in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """A single message in a conversation."""

    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """A conversation extracted from Google Gemini."""

    id: str
    title: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    url: Optional[str] = None
    status: ConversationStatus = ConversationStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Processing results
    summary: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)

    # Storage info
    file_path: Optional[str] = None
    file_size: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Conversation into a JSON-serializable dictionary.

        The returned dictionary includes all top-level fields and converts nested objects to simple types:
        - `messages` is a list of dictionaries with `role` as the enum value string, `timestamp` as an ISO 8601 string or `None`, `content`, and `metadata`.
        - `created_at` and `updated_at` are ISO 8601 strings.
        - Enum fields such as `status` are represented by their value strings.

        Returns:
            dict: A dictionary representation of the conversation suitable for JSON serialization.

        """
        return {
            "id": self.id,
            "title": self.title,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "metadata": msg.metadata,
                }
                for msg in self.messages
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "url": self.url,
            "status": self.status.value,
            "metadata": self.metadata,
            "summary": self.summary,
            "keywords": self.keywords,
            "tags": self.tags,
            "topics": self.topics,
            "file_path": self.file_path,
            "file_size": self.file_size,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Constructs a Conversation object from a dictionary representation.

        Parameters
        ----------
            data (Dict[str, Any]): Dictionary containing conversation fields. Expected keys include:
                - "id", "title", "created_at", "updated_at"
                - "messages": list of message dicts with keys "role", "content", optional "timestamp" (ISO string) and optional "metadata"
                - optional keys: "url", "status", "metadata", "summary", "keywords", "tags", "topics", "file_path", "file_size"

        Description:
            Rebuilds Message objects from the "messages" list, parses ISO-formatted timestamps, converts string values to the appropriate enum members for roles and conversation status, and applies sensible defaults for missing optional fields.

        Returns
        -------
            Conversation: A Conversation instance populated from the provided dictionary.

        """
        messages = [
            Message(
                role=MessageRole(msg_data["role"]),
                content=msg_data["content"],
                timestamp=(
                    datetime.fromisoformat(msg_data["timestamp"])
                    if msg_data.get("timestamp")
                    else None
                ),
                metadata=msg_data.get("metadata", {}),
            )
            for msg_data in data.get("messages", [])
        ]

        return cls(
            id=data["id"],
            title=data["title"],
            messages=messages,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            url=data.get("url"),
            status=ConversationStatus(data.get("status", "pending")),
            metadata=data.get("metadata", {}),
            summary=data.get("summary"),
            keywords=data.get("keywords", []),
            tags=data.get("tags", []),
            topics=data.get("topics", []),
            file_path=data.get("file_path"),
            file_size=data.get("file_size"),
        )


@dataclass
class ExtractionResult:
    """Result of a conversation extraction run."""

    success: bool
    conversations_extracted: int
    conversations_processed: int
    conversations_failed: int
    total_messages: int
    start_time: datetime
    end_time: datetime
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """Return the extraction duration in seconds.

        Returns:
            float: The difference between `end_time` and `start_time` expressed in seconds. May be negative if `end_time` is earlier than `start_time`.

        """
        return (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the extraction result into a JSON-serializable dictionary.

        The dictionary contains ISO 8601 formatted timestamps for `start_time` and `end_time`, and a numeric `duration` in seconds computed from those timestamps.

        Returns:
            dict: Mapping with the following keys:
                - `success` (bool): Whether the extraction run succeeded.
                - `conversations_extracted` (int): Number of conversations extracted.
                - `conversations_processed` (int): Number of conversations processed.
                - `conversations_failed` (int): Number of conversations that failed.
                - `total_messages` (int): Total number of messages processed.
                - `start_time` (str): ISO 8601 string for the start time.
                - `end_time` (str): ISO 8601 string for the end time.
                - `duration` (float): Elapsed time in seconds between end and start.
                - `errors` (list[str]): Collected error messages.
                - `warnings` (list[str]): Collected warning messages.

        """
        return {
            "success": self.success,
            "conversations_extracted": self.conversations_extracted,
            "conversations_processed": self.conversations_processed,
            "conversations_failed": self.conversations_failed,
            "total_messages": self.total_messages,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass
class KnowledgeEntry:
    """A processed knowledge entry from conversations."""

    id: str
    title: str
    content: str
    source_conversation_id: str
    source_message_index: int
    created_at: datetime
    updated_at: datetime
    entry_type: str = "insight"  # insight, fact, question, answer, code, etc.
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the KnowledgeEntry into a JSON-serializable dictionary.

        The returned dictionary contains all public fields. Datetime fields `created_at` and `updated_at` are formatted as ISO 8601 strings.

        Returns:
            dict: Mapping of field names to their serialized values (e.g. `id`, `title`, `content`, `source_conversation_id`, `source_message_index`, `created_at`, `updated_at`, `entry_type`, `confidence`, `tags`, `keywords`, `metadata`).

        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "source_conversation_id": self.source_conversation_id,
            "source_message_index": self.source_message_index,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "entry_type": self.entry_type,
            "confidence": self.confidence,
            "tags": self.tags,
            "keywords": self.keywords,
            "metadata": self.metadata,
        }
