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
from app.summarization.strategies.execution import StrategyExecutor
from app.summarization.strategies.models import (
    StrategySelection,
    # StrategySelectionConfig,
    StrategySelectionInput,
    StrategyExecutionResult,
)
from app.summarization.strategies.selector import (
    SummarizationStrategySelector,
)


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
    ) -> None:
        self._chunker = chunker
        self._selector = selector or SummarizationStrategySelector()
        self._executor = executor or StrategyExecutor()

    def run(
        self,
        text: str,
        summarize: Callable[[str], str],
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

        chunks = self._chunker.chunk(text)

        token_count = sum(chunk.token_count for chunk in chunks)

        selection_input = StrategySelectionInput(
            token_count=token_count,
            chunk_count=len(chunks),
        )

        selection = self._selector.select(selection_input)

        execution = self._executor.execute(
            selection.strategy,
            chunks,
            summarize,
        )

        return SummarizationPipelineResult(
            summary=execution.content,
            selection=selection,
            execution=execution,
            chunk_count=len(chunks),
            token_count=token_count,
        )
