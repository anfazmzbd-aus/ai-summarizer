"""V11 async integration adapter for the existing V9 summarization pipeline."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from app.summarization.intelligence import SummarizationIntent
from app.summarization.pipeline import (
    SummarizationPipeline,
    SummarizationPipelineResult,
)


AsyncSummarizer = Callable[[str], Awaitable[str]]


class AsyncSummarizationPipelineAdapter:
    """
    Adapt the synchronous, provider-independent V9 pipeline to the
    asynchronous V11 application composition boundary.

    The V9 pipeline and strategy implementations remain unchanged.

    Pipeline execution occurs in a worker thread. Each synchronous
    strategy callback is safely marshalled back to the application's
    running event loop where the asynchronous summarizer executes.
    """

    def __init__(
        self,
        pipeline: SummarizationPipeline,
    ) -> None:
        if not isinstance(pipeline, SummarizationPipeline):
            raise TypeError("pipeline must be a SummarizationPipeline")

        self._pipeline = pipeline

    @property
    def pipeline(self) -> SummarizationPipeline:
        """Return the wrapped V9 pipeline."""

        return self._pipeline

    async def run(
        self,
        text: str,
        summarize: AsyncSummarizer,
        *,
        intent: SummarizationIntent | str | None = None,
    ) -> SummarizationPipelineResult:
        """
        Execute the existing V9 pipeline using an async summarizer.

        No provider-specific behavior is introduced here.
        """

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not callable(summarize):
            raise TypeError("summarize must be callable")

        loop = asyncio.get_running_loop()

        def summarize_sync(source: str) -> str:
            future = asyncio.run_coroutine_threadsafe(
                summarize(source),
                loop,
            )

            return future.result()

        return await asyncio.to_thread(
            self._pipeline.run,
            text,
            summarize_sync,
            intent=intent,
        )
