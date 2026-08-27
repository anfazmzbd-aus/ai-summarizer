"""Tests for V11 V9-pipeline construction."""

from app.core.summarization_pipeline_adapter import (
    AsyncSummarizationPipelineAdapter,
)
from app.core.summarization_pipeline_factory import (
    build_summarization_pipeline_adapter,
)
from app.summarization.pipeline import SummarizationPipeline


def test_factory_builds_async_pipeline_adapter() -> None:
    adapter = build_summarization_pipeline_adapter()

    assert isinstance(
        adapter,
        AsyncSummarizationPipelineAdapter,
    )


def test_factory_wraps_existing_v9_pipeline() -> None:
    adapter = build_summarization_pipeline_adapter()

    assert isinstance(
        adapter.pipeline,
        SummarizationPipeline,
    )
