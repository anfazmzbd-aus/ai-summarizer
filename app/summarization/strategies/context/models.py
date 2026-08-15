"""
Models for context-preserving summarization aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# from app.summarization.strategies.models import MapResult


@dataclass(frozen=True)
class ContextEnvelope:
    """
    Contextual representation of a mapped chunk.

    The envelope preserves both the generated summary and the source
    information required to reconstruct document context.
    """

    chunk_index: int
    summary: str
    source_text: str
    start_offset: int
    end_offset: int
    token_count: int
    character_count: int
    preceding_chunk_index: int | None = None
    following_chunk_index: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be non-negative")

        if not isinstance(self.summary, str):
            raise TypeError("summary must be a string")

        if not isinstance(self.source_text, str):
            raise TypeError("source_text must be a string")

        if self.start_offset < 0:
            raise ValueError("start_offset must be non-negative")

        if self.end_offset < self.start_offset:
            raise ValueError("end_offset must be greater than or equal to start_offset")

        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        if self.character_count < 0:
            raise ValueError("character_count must be non-negative")

        if self.preceding_chunk_index is not None and self.preceding_chunk_index < 0:
            raise ValueError("preceding_chunk_index must be non-negative")

        if self.following_chunk_index is not None and self.following_chunk_index < 0:
            raise ValueError("following_chunk_index must be non-negative")


@dataclass(frozen=True)
class AggregatedContext:
    """
    Ordered collection of contextualized MAP results.
    """

    envelopes: tuple[ContextEnvelope, ...]
    source_chunk_indexes: tuple[int, ...]
    start_offset: int
    end_offset: int
    total_tokens: int
    total_characters: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        indexes = tuple(envelope.chunk_index for envelope in self.envelopes)

        if indexes != self.source_chunk_indexes:
            raise ValueError("source_chunk_indexes must match envelope order")

        if self.start_offset < 0:
            raise ValueError("start_offset must be non-negative")

        if self.end_offset < self.start_offset:
            raise ValueError("end_offset must be greater than or equal to start_offset")

        if self.total_tokens < 0:
            raise ValueError("total_tokens must be non-negative")

        if self.total_characters < 0:
            raise ValueError("total_characters must be non-negative")

    @classmethod
    def empty(cls) -> "AggregatedContext":
        """Create an empty aggregated context."""
        return cls(
            envelopes=(),
            source_chunk_indexes=(),
            start_offset=0,
            end_offset=0,
            total_tokens=0,
            total_characters=0,
            metadata={
                "chunk_count": 0,
            },
        )
