"""
Provider-independent strategy execution dispatcher.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Callable

from app.summarization.chunking.models import Chunk

from .models import (
    StrategyExecutionResult,
    SummarizationStrategyType,
)
from .strategy import (
    DirectSummarizationStrategy,
    HierarchicalSummarizationStrategy,
    MapReduceSummarizationStrategy,
    SummarizationStrategy,
)


class StrategyExecutor:
    """
    Dispatches a selected strategy without knowing anything about
    providers or runtime contracts.
    """

    def __init__(
        self,
        strategies: (
            dict[
                SummarizationStrategyType,
                SummarizationStrategy,
            ]
            | None
        ) = None,
    ) -> None:
        self._strategies = strategies or {
            SummarizationStrategyType.DIRECT: (DirectSummarizationStrategy()),
            SummarizationStrategyType.MAP_REDUCE: (MapReduceSummarizationStrategy()),
            SummarizationStrategyType.HIERARCHICAL: (
                HierarchicalSummarizationStrategy()
            ),
        }

    def execute(
        self,
        strategy: SummarizationStrategyType,
        chunks: Sequence[Chunk],
        summarize: Callable[[str], str],
    ) -> StrategyExecutionResult:
        if not isinstance(
            strategy,
            SummarizationStrategyType,
        ):
            raise ValueError(f"unsupported strategy: {strategy}")

        implementation = self._strategies.get(strategy)

        if implementation is None:
            raise ValueError(
                f"no implementation registered for strategy: " f"{strategy.value}"
            )

        return implementation.execute(
            chunks,
            summarize,
        )

    def registered_strategies(
        self,
    ) -> tuple[SummarizationStrategyType, ...]:
        """Return registered strategies in deterministic order."""

        return tuple(
            strategy
            for strategy in SummarizationStrategyType
            if strategy in self._strategies
        )
