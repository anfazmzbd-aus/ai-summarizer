"""
Models used by the V9.2 Map-Reduce summarization strategy.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import Enum

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


"""
V9.2-M7 Models for advanced summarization strategy selection and execution.
"""


class SummarizationStrategyType(str, Enum):
    """Supported high-level summarization strategies."""

    DIRECT = "direct"
    MAP_REDUCE = "map_reduce"
    HIERARCHICAL = "hierarchical"


@dataclass(frozen=True)
class StrategySelectionConfig:
    """
    Deterministic thresholds used by the strategy selector.

    Selection rules:

        chunk_count == 0
            -> DIRECT

        token_count <= direct_max_tokens
            -> DIRECT

        token_count <= map_reduce_max_tokens
            -> MAP_REDUCE

        otherwise
            -> HIERARCHICAL
    """

    direct_max_tokens: int = 2_000
    map_reduce_max_tokens: int = 10_000

    def __post_init__(self) -> None:
        if self.direct_max_tokens <= 0:
            raise ValueError("direct_max_tokens must be greater than zero")

        if self.map_reduce_max_tokens <= 0:
            raise ValueError("map_reduce_max_tokens must be greater than zero")

        if self.map_reduce_max_tokens <= self.direct_max_tokens:
            raise ValueError(
                "map_reduce_max_tokens must be greater than " "direct_max_tokens"
            )


@dataclass(frozen=True)
class StrategySelectionInput:
    """
    Normalized document characteristics used for strategy selection.
    """

    token_count: int
    chunk_count: int

    def __post_init__(self) -> None:
        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        if self.chunk_count < 0:
            raise ValueError("chunk_count must be non-negative")


@dataclass(frozen=True)
class StrategySelection:
    """
    Result of deterministic strategy selection.
    """

    strategy: SummarizationStrategyType
    token_count: int
    chunk_count: int
    reason: str
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        if self.chunk_count < 0:
            raise ValueError("chunk_count must be non-negative")

        if not self.reason:
            raise ValueError("reason must not be empty")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")


@dataclass(frozen=True)
class StrategyExecutionResult:
    """
    Provider-independent result returned by strategy execution.
    """

    strategy: SummarizationStrategyType
    content: str
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise TypeError("content must be a string")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")
