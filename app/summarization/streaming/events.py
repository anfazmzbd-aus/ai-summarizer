"""
Typed streaming lifecycle events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import StreamEventType


@dataclass(frozen=True)
class StreamStartedEvent:
    """Marks the beginning of a stream."""

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def event_type(self) -> StreamEventType:
        return StreamEventType.STARTED


@dataclass(frozen=True)
class StreamChunkEvent:
    """
    Represents one ordered piece of streamed content.
    """

    sequence: int
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")

        if not isinstance(self.content, str):
            raise TypeError("content must be a string")

    @property
    def event_type(self) -> StreamEventType:
        return StreamEventType.CHUNK


@dataclass(frozen=True)
class StreamCompletedEvent:
    """Marks successful stream completion."""

    content: str
    chunk_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise TypeError("content must be a string")

        if self.chunk_count < 0:
            raise ValueError("chunk_count must be non-negative")

    @property
    def event_type(self) -> StreamEventType:
        return StreamEventType.COMPLETED


@dataclass(frozen=True)
class StreamErrorEvent:
    """Marks stream termination due to an error."""

    error_type: str
    message: str
    sequence: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")

        if not self.error_type:
            raise ValueError("error_type must not be empty")

        if not self.message:
            raise ValueError("message must not be empty")

    @property
    def event_type(self) -> StreamEventType:
        return StreamEventType.ERROR


__all__ = [
    "StreamChunkEvent",
    "StreamCompletedEvent",
    "StreamErrorEvent",
    "StreamStartedEvent",
]
