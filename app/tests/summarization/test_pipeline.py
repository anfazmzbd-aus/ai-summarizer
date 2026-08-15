"""
Regression and integration tests for the V9.2 summarization pipeline.
"""

from __future__ import annotations

import pytest

from app.summarization.chunking.models import ChunkingConfig
from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.pipeline import (
    SummarizationPipeline,
    SummarizationPipelineResult,
)
from app.summarization.strategies.models import (
    StrategySelectionConfig,
    SummarizationStrategyType,
)
from app.summarization.strategies.selector import (
    SummarizationStrategySelector,
)


def summarize(text: str) -> str:
    """
    Deterministic test summarizer.

    No provider or network dependency is involved.
    """
    return f"SUMMARY:{text}"


def make_pipeline(
    *,
    max_tokens: int = 5,
    direct_max_tokens: int = 5,
    map_reduce_max_tokens: int = 20,
) -> SummarizationPipeline:
    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=max_tokens,
            overlap_tokens=0,
        )
    )

    selector = SummarizationStrategySelector(
        StrategySelectionConfig(
            direct_max_tokens=direct_max_tokens,
            map_reduce_max_tokens=map_reduce_max_tokens,
        )
    )

    return SummarizationPipeline(
        chunker=chunker,
        selector=selector,
    )


def test_empty_document_produces_empty_pipeline_result():
    pipeline = make_pipeline()

    result = pipeline.run("", summarize)

    assert isinstance(
        result,
        SummarizationPipelineResult,
    )
    assert result.summary == ""
    assert result.chunk_count == 0
    assert result.token_count == 0
    assert result.selection.strategy is SummarizationStrategyType.DIRECT


def test_small_document_uses_direct_strategy():
    pipeline = make_pipeline(
        max_tokens=10,
        direct_max_tokens=10,
        map_reduce_max_tokens=20,
    )

    result = pipeline.run(
        "one two three",
        summarize,
    )

    assert result.selection.strategy is SummarizationStrategyType.DIRECT

    assert result.chunk_count == 1
    assert result.token_count == 3


def test_medium_document_uses_map_reduce_strategy():
    pipeline = make_pipeline(
        max_tokens=3,
        direct_max_tokens=3,
        map_reduce_max_tokens=10,
    )

    result = pipeline.run(
        "one two three four five six",
        summarize,
    )

    assert result.selection.strategy is SummarizationStrategyType.MAP_REDUCE

    assert result.chunk_count == 2
    assert result.token_count == 6


def test_large_document_uses_hierarchical_strategy():
    pipeline = make_pipeline(
        max_tokens=2,
        direct_max_tokens=2,
        map_reduce_max_tokens=4,
    )

    result = pipeline.run(
        "one two three four five six seven eight",
        summarize,
    )

    assert result.selection.strategy is SummarizationStrategyType.HIERARCHICAL

    assert result.chunk_count == 4
    assert result.token_count == 8


def test_chunk_order_is_preserved_through_pipeline():
    calls: list[str] = []

    def recording_summarize(text: str) -> str:
        calls.append(text)
        return text.upper()

    pipeline = make_pipeline(
        max_tokens=2,
        direct_max_tokens=1,
        map_reduce_max_tokens=10,
    )

    pipeline.run(
        "alpha beta gamma delta",
        recording_summarize,
    )

    assert calls[:2] == [
        "alpha beta",
        "gamma delta",
    ]


def test_pipeline_is_deterministic():
    pipeline = make_pipeline(
        max_tokens=3,
        direct_max_tokens=3,
        map_reduce_max_tokens=10,
    )

    text = "one two three four five six"

    first = pipeline.run(text, summarize)
    second = pipeline.run(text, summarize)

    assert first == second


def test_pipeline_preserves_token_count():
    pipeline = make_pipeline(
        max_tokens=3,
    )

    result = pipeline.run(
        "one two three four five",
        summarize,
    )

    assert result.token_count == 5


def test_pipeline_preserves_chunk_count():
    pipeline = make_pipeline(
        max_tokens=2,
    )

    result = pipeline.run(
        "one two three four five",
        summarize,
    )

    assert result.chunk_count == 3


def test_pipeline_result_summary_matches_execution():
    pipeline = make_pipeline()

    result = pipeline.run(
        "hello world",
        summarize,
    )

    assert result.summary == result.execution.content


def test_pipeline_result_contains_strategy_metadata():
    pipeline = make_pipeline()

    result = pipeline.run(
        "hello world",
        summarize,
    )

    assert result.selection.reason
    assert result.selection.metadata["direct_max_tokens"] == 5


def test_pipeline_rejects_non_string_document():
    pipeline = make_pipeline()

    with pytest.raises(
        TypeError,
        match="text must be a string",
    ):
        pipeline.run(
            None,  # type: ignore[arg-type]
            summarize,
        )


def test_pipeline_rejects_non_callable_summarizer():
    pipeline = make_pipeline()

    with pytest.raises(
        TypeError,
        match="summarize must be callable",
    ):
        pipeline.run(
            "hello world",
            None,  # type: ignore[arg-type]
        )


def test_pipeline_propagates_summarizer_failure():
    pipeline = make_pipeline()

    def failing_summarizer(text: str) -> str:
        raise RuntimeError("summarization failed")

    with pytest.raises(
        RuntimeError,
        match="summarization failed",
    ):
        pipeline.run(
            "hello world",
            failing_summarizer,
        )


def test_pipeline_propagates_invalid_summarizer_result():
    pipeline = make_pipeline()

    def invalid_summarizer(text: str) -> str:
        return None  # type: ignore[return-value]

    with pytest.raises(
        TypeError,
        match="must return a string",
    ):
        pipeline.run(
            "hello world",
            invalid_summarizer,
        )


def test_pipeline_supports_exact_direct_boundary():
    pipeline = make_pipeline(
        max_tokens=10,
        direct_max_tokens=3,
        map_reduce_max_tokens=10,
    )

    result = pipeline.run(
        "one two three",
        summarize,
    )

    assert result.selection.strategy is SummarizationStrategyType.DIRECT


def test_pipeline_supports_exact_map_reduce_boundary():
    pipeline = make_pipeline(
        max_tokens=3,
        direct_max_tokens=2,
        map_reduce_max_tokens=6,
    )

    result = pipeline.run(
        "one two three four five six",
        summarize,
    )

    assert result.selection.strategy is SummarizationStrategyType.MAP_REDUCE


def test_pipeline_selects_hierarchy_after_map_reduce_boundary():
    pipeline = make_pipeline(
        max_tokens=3,
        direct_max_tokens=2,
        map_reduce_max_tokens=5,
    )

    result = pipeline.run(
        "one two three four five six",
        summarize,
    )

    assert result.selection.strategy is SummarizationStrategyType.HIERARCHICAL


def test_pipeline_handles_single_token_document():
    pipeline = make_pipeline(
        max_tokens=5,
    )

    result = pipeline.run(
        "hello",
        summarize,
    )

    assert result.chunk_count == 1
    assert result.token_count == 1


def test_pipeline_handles_multiple_chunks():
    pipeline = make_pipeline(
        max_tokens=2,
        direct_max_tokens=2,
        map_reduce_max_tokens=10,
    )

    result = pipeline.run(
        "one two three four five six",
        summarize,
    )

    assert result.chunk_count == 3
    assert result.token_count == 6


def test_pipeline_does_not_require_provider_configuration():
    pipeline = make_pipeline()

    result = pipeline.run(
        "provider independent test",
        summarize,
    )

    assert result.summary.startswith("SUMMARY:")


def test_pipeline_uses_existing_chunker():
    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=2,
            overlap_tokens=0,
        )
    )

    pipeline = SummarizationPipeline(
        chunker=chunker,
    )

    result = pipeline.run(
        "one two three four",
        summarize,
    )

    assert result.chunk_count == 2


def test_pipeline_result_is_immutable():
    pipeline = make_pipeline()

    result = pipeline.run(
        "hello world",
        summarize,
    )

    with pytest.raises(
        AttributeError,
    ):
        result.summary = "changed"  # type: ignore[misc]
