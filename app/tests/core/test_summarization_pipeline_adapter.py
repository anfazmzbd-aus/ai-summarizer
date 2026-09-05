"""Tests for the V11 async V9-pipeline integration adapter."""

from __future__ import annotations

import pytest
import asyncio

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
from app.core.summarization_pipeline_factory import (
    build_summarization_pipeline_adapter,
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


@pytest.mark.anyio
async def test_adapter_does_not_retry_summarizer_timeout() -> None:
    summarize_calls = 0

    async def timeout_summarize(text: str) -> str:
        nonlocal summarize_calls
        summarize_calls += 1
        raise TimeoutError("provider timeout")

    adapter = AsyncSummarizationPipelineAdapter(
        SummarizationPipeline(
            chunker=TextChunker(),
        )
    )

    with pytest.raises(
        TimeoutError,
        match="provider timeout",
    ):
        await adapter.run(
            text="Short source text.",
            summarize=timeout_summarize,
        )

    assert summarize_calls == 1


@pytest.mark.anyio
async def test_adapter_supports_concurrent_independent_requests() -> None:
    adapter = build_summarization_pipeline_adapter()

    calls: list[str] = []

    async def summarize(source: str) -> str:
        calls.append(source)

        await asyncio.sleep(0)

        return f"summary:{source}"

    results = await asyncio.gather(
        adapter.run(
            "first source",
            summarize,
        ),
        adapter.run(
            "second source",
            summarize,
        ),
        adapter.run(
            "third source",
            summarize,
        ),
    )

    assert len(results) == 3

    assert all(result.summary for result in results)

    assert all(result.execution.content == result.summary for result in results)

    assert len(calls) == 3

    assert set(calls) == {
        "first source",
        "second source",
        "third source",
    }


@pytest.mark.anyio
async def test_adapter_preserves_request_isolation_under_interleaving() -> None:
    adapter = build_summarization_pipeline_adapter()

    delays = {
        "slow source": 0.03,
        "medium source": 0.02,
        "fast source": 0.01,
    }

    async def summarize(source: str) -> str:
        await asyncio.sleep(delays[source])
        return f"summary:{source}"

    slow_result, medium_result, fast_result = await asyncio.gather(
        adapter.run(
            "slow source",
            summarize,
        ),
        adapter.run(
            "medium source",
            summarize,
        ),
        adapter.run(
            "fast source",
            summarize,
        ),
    )

    assert slow_result.summary == "summary:slow source"
    assert medium_result.summary == "summary:medium source"
    assert fast_result.summary == "summary:fast source"

    assert slow_result.execution.content == slow_result.summary
    assert medium_result.execution.content == medium_result.summary
    assert fast_result.execution.content == fast_result.summary


@pytest.mark.anyio
async def test_adapter_isolates_failure_between_concurrent_requests() -> None:
    adapter = build_summarization_pipeline_adapter()

    async def summarize(source: str) -> str:
        await asyncio.sleep(0)

        if source == "failing source":
            raise RuntimeError("isolated failure")

        return f"summary:{source}"

    results = await asyncio.gather(
        adapter.run(
            "first source",
            summarize,
        ),
        adapter.run(
            "failing source",
            summarize,
        ),
        adapter.run(
            "third source",
            summarize,
        ),
        return_exceptions=True,
    )

    first_result, failed_result, third_result = results

    assert first_result.summary == "summary:first source"
    assert isinstance(failed_result, RuntimeError)
    assert str(failed_result) == "isolated failure"
    assert third_result.summary == "summary:third source"

    assert first_result.execution.content == first_result.summary
    assert third_result.execution.content == third_result.summary


@pytest.mark.anyio
async def test_adapter_remains_stable_across_repeated_concurrent_batches() -> None:
    adapter = build_summarization_pipeline_adapter()

    async def summarize(source: str) -> str:
        await asyncio.sleep(0)
        return f"summary:{source}"

    for batch in range(5):
        sources = [
            f"batch-{batch}-source-1",
            f"batch-{batch}-source-2",
            f"batch-{batch}-source-3",
        ]

        results = await asyncio.gather(
            *(
                adapter.run(
                    source,
                    summarize,
                )
                for source in sources
            )
        )

        assert [result.summary for result in results] == [
            f"summary:{source}" for source in sources
        ]

        assert all(result.execution.content == result.summary for result in results)
