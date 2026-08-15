"""
V9.3-M1 models for deterministic summarization planning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.summarization.chunking.models import Chunk
from app.summarization.strategies.models import (
    StrategySelection,
    SummarizationStrategyType,
)


@dataclass(frozen=True)
class SummarizationPlan:
    """
    Immutable execution plan produced before summarization execution.

    The plan contains the deterministic document preparation and existing
    V9.2 strategy selection result. It does not contain provider state or
    invoke any external service.
    """

    strategy: SummarizationStrategyType
    selection: StrategySelection
    chunks: tuple[Chunk, ...]
    token_count: int
    chunk_count: int
    source_character_count: int
    source_digest: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.strategy, SummarizationStrategyType):
            raise TypeError("strategy must be a SummarizationStrategyType")

        if self.strategy is not self.selection.strategy:
            raise ValueError("strategy must match selection.strategy")

        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        if self.chunk_count < 0:
            raise ValueError("chunk_count must be non-negative")

        if self.chunk_count != len(self.chunks):
            raise ValueError("chunk_count must match the number of chunks")

        if self.token_count != sum(chunk.token_count for chunk in self.chunks):
            raise ValueError("token_count must match chunk token counts")

        if self.selection.token_count != self.token_count:
            raise ValueError("selection token_count must match plan token_count")

        if self.selection.chunk_count != self.chunk_count:
            raise ValueError("selection chunk_count must match plan chunk_count")

        if self.source_character_count < 0:
            raise ValueError("source_character_count must be non-negative")

        if not isinstance(self.source_digest, str) or not self.source_digest:
            raise ValueError("source_digest must not be empty")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")
