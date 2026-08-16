"""
V9.2 summarization pipeline.

Composes the independently tested V9.2 summarization components:

    document
        -> chunking
        -> strategy selection
        -> strategy execution

The pipeline is intentionally provider-independent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.planning import SummarizationPlanner
from app.summarization.strategies.execution import StrategyExecutor
from app.summarization.strategies.models import (
    StrategySelection,
    # StrategySelectionConfig,
    StrategyExecutionResult,
)
from app.summarization.strategies.selector import SummarizationStrategySelector
from app.summarization.intelligence import SummarizationIntent


@dataclass(frozen=True)
class SummarizationPipelineResult:
    """
    Deterministic result produced by the V9.2 pipeline.
    """

    summary: str
    selection: StrategySelection
    execution: StrategyExecutionResult
    chunk_count: int
    token_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.summary, str):
            raise TypeError("summary must be a string")

        if self.chunk_count < 0:
            raise ValueError("chunk_count must be non-negative")

        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        if self.execution.content != self.summary:
            raise ValueError("summary must match execution content")


class SummarizationPipeline:
    """
    Provider-independent V9.2 summarization pipeline.

    The pipeline owns composition only. Chunking, strategy selection,
    and strategy execution remain independently testable components.
    """

    def __init__(
        self,
        chunker: TextChunker,
        selector: SummarizationStrategySelector | None = None,
        executor: StrategyExecutor | None = None,
        planner: SummarizationPlanner | None = None,
    ) -> None:
        self._chunker = chunker
        self._selector = selector or SummarizationStrategySelector()
        self._executor = executor or StrategyExecutor()
        self._planner = planner or SummarizationPlanner(
            chunker=self._chunker,
            selector=self._selector,
        )

    def run(
        self,
        text: str,
        summarize: Callable[[str], str],
        *,
        intent: SummarizationIntent | str | None = None,
    ) -> SummarizationPipelineResult:
        """
        Execute the complete V9.2 summarization pipeline.

        Parameters
        ----------
        text:
            Source document.
        summarize:
            Provider-independent summarization callable.

        Returns
        -------
        SummarizationPipelineResult
            Deterministic pipeline result containing selection,
            execution, and document metrics.
        """

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not callable(summarize):
            raise TypeError("summarize must be callable")

        plan = self._planner.plan(text, intent=intent)

        execution = self._executor.execute(
            plan.strategy,
            plan.chunks,
            summarize,
        )

        return SummarizationPipelineResult(
            summary=execution.content,
            selection=plan.selection,
            execution=execution,
            chunk_count=plan.chunk_count,
            token_count=plan.token_count,
        )
