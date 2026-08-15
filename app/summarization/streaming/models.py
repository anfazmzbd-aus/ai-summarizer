"""
Models for provider-independent summarization streaming.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StreamEventType(str, Enum):
    """Lifecycle events emitted by the streaming layer."""

    STARTED = "started"
    CHUNK = "chunk"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass(frozen=True)
class StreamResult:
    """
    Final deterministic representation of a completed stream.
    """

    content: str
    chunk_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise TypeError("content must be a string")

        if self.chunk_count < 0:
            raise ValueError("chunk_count must be non-negative")
