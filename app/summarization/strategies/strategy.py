"""
Strategy abstractions for advanced summarization.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.summarization.chunking.models import Chunk

from .models import (
    StrategyExecutionResult,
    SummarizationStrategyType,
)


class SummarizationStrategy(ABC):
    """
    Provider-independent summarization strategy contract.

    Concrete strategies receive already-prepared chunks and delegate
    actual summarization behavior through an injected callable.
    """

    strategy_type: SummarizationStrategyType

    @abstractmethod
    def execute(
        self,
        chunks: Sequence[Chunk],
        summarize: callable,
    ) -> StrategyExecutionResult:
        """
        Execute the strategy against the supplied chunks.
        """
        raise NotImplementedError


class DirectSummarizationStrategy(SummarizationStrategy):
    """Summarize the complete input as one unit."""

    strategy_type = SummarizationStrategyType.DIRECT

    def execute(
        self,
        chunks: Sequence[Chunk],
        summarize: callable,
    ) -> StrategyExecutionResult:
        if not callable(summarize):
            raise TypeError("summarize must be callable")

        if not chunks:
            content = ""
        else:
            source = "".join(chunk.text for chunk in chunks)
            content = summarize(source)

        if not isinstance(content, str):
            raise TypeError("summarize must return a string")

        return StrategyExecutionResult(
            strategy=self.strategy_type,
            content=content,
            metadata={
                "chunk_count": len(chunks),
            },
        )


class MapReduceSummarizationStrategy(SummarizationStrategy):
    """
    Adapter around the existing M4 map-reduce implementation.

    The implementation remains intentionally lightweight at M7.
    """

    strategy_type = SummarizationStrategyType.MAP_REDUCE

    def execute(
        self,
        chunks: Sequence[Chunk],
        summarize: callable,
    ) -> StrategyExecutionResult:
        if not callable(summarize):
            raise TypeError("summarize must be callable")

        mapped: list[str] = []

        for chunk in chunks:
            result = summarize(chunk.text)

            if not isinstance(result, str):
                raise TypeError("summarize must return a string")

            mapped.append(result)

        reduced = summarize("\n".join(mapped))

        if not isinstance(reduced, str):
            raise TypeError("summarize must return a string")

        return StrategyExecutionResult(
            strategy=self.strategy_type,
            content=reduced,
            metadata={
                "chunk_count": len(chunks),
                "map_count": len(mapped),
            },
        )


class HierarchicalSummarizationStrategy(SummarizationStrategy):
    """
    Provider-independent hierarchical strategy.

    Hierarchical grouping remains delegated to the existing hierarchy
    layer. M7 only establishes the strategy boundary.
    """

    strategy_type = SummarizationStrategyType.HIERARCHICAL

    def execute(
        self,
        chunks: Sequence[Chunk],
        summarize: callable,
    ) -> StrategyExecutionResult:
        if not callable(summarize):
            raise TypeError("summarize must be callable")

        if not chunks:
            return StrategyExecutionResult(
                strategy=self.strategy_type,
                content="",
                metadata={
                    "chunk_count": 0,
                },
            )

        current = [summarize(chunk.text) for chunk in chunks]

        for result in current:
            if not isinstance(result, str):
                raise TypeError("summarize must return a string")

        while len(current) > 1:
            next_level: list[str] = []

            for index in range(0, len(current), 2):
                group = current[index : index + 2]
                combined = "\n".join(group)

                result = summarize(combined)

                if not isinstance(result, str):
                    raise TypeError("summarize must return a string")

                next_level.append(result)

            current = next_level

        return StrategyExecutionResult(
            strategy=self.strategy_type,
            content=current[0],
            metadata={
                "chunk_count": len(chunks),
            },
        )
