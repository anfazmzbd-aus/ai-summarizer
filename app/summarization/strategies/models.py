"""
Models used by the V9.2 Map-Reduce summarization strategy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MapResult:
    """
    Result produced by one MAP operation.

    A MapResult retains the source chunk index so provenance remains
    available throughout the Map-Reduce pipeline.
    """

    chunk_index: int
    summary: str
    token_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be non-negative")

        if not isinstance(self.summary, str):
            raise TypeError("summary must be a string")

        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")


@dataclass(frozen=True)
class ReduceInput:
    """
    Ordered collection of MAP results supplied to the REDUCE operation.
    """

    results: tuple[MapResult, ...]
    source_chunk_indexes: tuple[int, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.results) != len(self.source_chunk_indexes):
            raise ValueError("results and source_chunk_indexes must have equal lengths")

        indexes = tuple(result.chunk_index for result in self.results)

        if indexes != self.source_chunk_indexes:
            raise ValueError("source_chunk_indexes must match the ordered MAP results")


@dataclass(frozen=True)
class MapReduceResult:
    """
    Final result produced by the Map-Reduce strategy.
    """

    summary: str
    map_results: tuple[MapResult, ...]
    source_chunk_indexes: tuple[int, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.summary, str):
            raise TypeError("summary must be a string")

        indexes = tuple(result.chunk_index for result in self.map_results)

        if indexes != self.source_chunk_indexes:
            raise ValueError("source_chunk_indexes must match the ordered MAP results")
