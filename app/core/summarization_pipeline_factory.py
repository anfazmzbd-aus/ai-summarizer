"""V11 construction helpers for the existing V9 summarization pipeline."""

from __future__ import annotations

from app.core.summarization_pipeline_adapter import (
    AsyncSummarizationPipelineAdapter,
)
from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.pipeline import SummarizationPipeline


def build_summarization_pipeline_adapter() -> AsyncSummarizationPipelineAdapter:
    """
    Build the canonical V11 adapter around the existing V9 pipeline.

    Default V9 chunking, planning, selection, and execution policies
    remain authoritative.
    """

    pipeline = SummarizationPipeline(
        chunker=TextChunker(),
    )

    return AsyncSummarizationPipelineAdapter(
        pipeline,
    )
