"""
AI Summarizer V9.2

Models for token-aware document chunking.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """
    Immutable representation of a document chunk.

    Attributes:
        index: Zero-based position of the chunk in the source document.
        text: Exact source text represented by the chunk.
        token_count: Number of deterministic tokens in the chunk.
        character_count: Number of characters in the chunk.
        start_offset: Inclusive character offset in the source document.
        end_offset: Exclusive character offset in the source document.
    """

    index: int
    text: str
    token_count: int
    character_count: int
    start_offset: int
    end_offset: int

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("index must be non-negative")

        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        if self.character_count < 0:
            raise ValueError("character_count must be non-negative")

        if self.start_offset < 0:
            raise ValueError("start_offset must be non-negative")

        if self.end_offset < self.start_offset:
            raise ValueError("end_offset must not precede start_offset")

        if self.character_count != len(self.text):
            raise ValueError("character_count must match the length of text")

        if self.end_offset - self.start_offset != self.character_count:
            raise ValueError("source offsets must match the character count")


@dataclass(frozen=True)
class ChunkingConfig:
    """
    Configuration for token-aware text chunking.

    max_tokens:
        Maximum number of tokens permitted in a normal chunk.

    overlap_tokens:
        Number of trailing tokens reused as context at the beginning
        of the next chunk.

    preserve_boundaries:
        Prefer paragraph and sentence boundaries when selecting chunk
        endpoints. Oversized sentences are still split token-wise.
    """

    max_tokens: int = 512
    overlap_tokens: int = 0
    preserve_boundaries: bool = True

    def __post_init__(self) -> None:
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero")

        if self.overlap_tokens < 0:
            raise ValueError("overlap_tokens must be non-negative")

        if self.overlap_tokens >= self.max_tokens:
            raise ValueError("overlap_tokens must be smaller than max_tokens")
