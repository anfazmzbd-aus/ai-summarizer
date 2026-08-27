"""Tests for the V11 async V9-pipeline integration adapter."""

from __future__ import annotations

import pytest

from app.core.summarization_pipeline_adapter import (
    AsyncSummarizationPipelineAdapter,
)
from app.summarization.chunking.models import ChunkingConfig
from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.pipeline import SummarizationPipeline
from app.summarization.strategies.models import (
    StrategySelectionConfig,
    SummarizationStrategyType,
)
from app.summarization.strategies.selector import (
    SummarizationStrategySelector,
)


def make_adapter(
    *,
    max_tokens: int = 5,
    direct_max_tokens: int = 5,
    map_reduce_max_tokens: int = 20,
) -> AsyncSummarizationPipelineAdapter:
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

    pipeline = SummarizationPipeline(
        chunker=chunker,
        selector=selector,
    )

    return AsyncSummarizationPipelineAdapter(pipeline)


@pytest.mark.anyio
async def test_adapter_executes_existing_pipeline_with_async_summarizer() -> None:
    adapter = make_adapter()

    async def summarize(text: str) -> str:
        return f"SUMMARY:{text}"

    result = await adapter.run(
        "one two three",
        summarize,
    )

    assert result.summary == "SUMMARY:one two three"
    assert result.selection.strategy is SummarizationStrategyType.DIRECT


@pytest.mark.anyio
async def test_adapter_preserves_map_reduce_strategy() -> None:
    adapter = make_adapter(
        max_tokens=3,
        direct_max_tokens=3,
        map_reduce_max_tokens=10,
    )

    calls: list[str] = []

    async def summarize(text: str) -> str:
        calls.append(text)
        return f"SUMMARY:{text}"

    result = await adapter.run(
        "one two three four five six",
        summarize,
    )

    assert result.selection.strategy is SummarizationStrategyType.MAP_REDUCE
    assert result.chunk_count == 2

    # Two MAP calls plus one REDUCE call.
    assert len(calls) == 3


@pytest.mark.anyio
async def test_adapter_preserves_hierarchical_strategy() -> None:
    adapter = make_adapter(
        max_tokens=2,
        direct_max_tokens=2,
        map_reduce_max_tokens=4,
    )

    async def summarize(text: str) -> str:
        return f"SUMMARY:{text}"

    result = await adapter.run(
        "one two three four five six seven eight",
        summarize,
    )

    assert result.selection.strategy is SummarizationStrategyType.HIERARCHICAL
    assert result.chunk_count == 4


@pytest.mark.anyio
async def test_adapter_propagates_async_summarizer_failure() -> None:
    adapter = make_adapter()

    async def summarize(text: str) -> str:
        raise RuntimeError("provider failure")

    with pytest.raises(
        RuntimeError,
        match="provider failure",
    ):
        await adapter.run(
            "one two three",
            summarize,
        )


@pytest.mark.anyio
async def test_adapter_rejects_non_string_text() -> None:
    adapter = make_adapter()

    async def summarize(text: str) -> str:
        return text

    with pytest.raises(
        TypeError,
        match="text must be a string",
    ):
        await adapter.run(
            None,  # type: ignore[arg-type]
            summarize,
        )


@pytest.mark.anyio
async def test_adapter_rejects_non_callable_summarizer() -> None:
    adapter = make_adapter()

    with pytest.raises(
        TypeError,
        match="summarize must be callable",
    ):
        await adapter.run(
            "text",
            None,  # type: ignore[arg-type]
        )


def test_adapter_requires_existing_v9_pipeline() -> None:
    with pytest.raises(
        TypeError,
        match="pipeline must be a SummarizationPipeline",
    ):
        AsyncSummarizationPipelineAdapter(
            object(),  # type: ignore[arg-type]
        )


@pytest.mark.anyio
async def test_adapter_does_not_swallow_summarizer_failure() -> None:
    adapter = make_adapter()

    calls = 0

    async def summarize(text: str) -> str:
        nonlocal calls
        calls += 1
        raise RuntimeError("execution failure")

    with pytest.raises(
        RuntimeError,
        match="execution failure",
    ):
        await adapter.run(
            "one two three",
            summarize,
        )

    assert calls == 1
