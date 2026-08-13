"""
Tests for the V9.2 Map-Reduce summarization strategy.
"""

from __future__ import annotations

import pytest

from app.summarization.chunking.models import Chunk
from app.summarization.strategies.map_reduce import MapReduceStrategy


def make_chunk(
    index: int,
    text: str | None = None,
) -> Chunk:
    content = text or f"chunk-{index}"

    return Chunk(
        index=index,
        text=content,
        token_count=len(content.split()),
        character_count=len(content),
        start_offset=index * 10,
        end_offset=(index * 10) + len(content),
    )


def test_empty_input_returns_empty_result():
    map_calls: list[int] = []
    reduce_calls: list[tuple[str, ...]] = []

    def map_fn(chunk: Chunk) -> str:
        map_calls.append(chunk.index)
        return f"map-{chunk.index}"

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        reduce_calls.append(tuple(summaries))
        return "reduced"

    result = MapReduceStrategy(
        map_fn=map_fn,
        reduce_fn=reduce_fn,
    ).summarize([])

    assert result.summary == ""
    assert result.map_results == ()
    assert result.source_chunk_indexes == ()
    assert result.metadata["map_count"] == 0
    assert result.metadata["reduced"] is False

    assert map_calls == []
    assert reduce_calls == []


def test_single_chunk_produces_map_reduce_result():
    calls: list[int] = []

    def map_fn(chunk: Chunk) -> str:
        calls.append(chunk.index)
        return f"mapped-{chunk.index}"

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        return f"final:{summaries[0]}"

    chunk = make_chunk(0)

    result = MapReduceStrategy(
        map_fn=map_fn,
        reduce_fn=reduce_fn,
    ).summarize([chunk])

    assert calls == [0]
    assert result.summary == "final:mapped-0"
    assert len(result.map_results) == 1
    assert result.map_results[0].chunk_index == 0
    assert result.map_results[0].summary == "mapped-0"
    assert result.source_chunk_indexes == (0,)


def test_multiple_chunks_are_mapped_in_source_order():
    calls: list[int] = []

    def map_fn(chunk: Chunk) -> str:
        calls.append(chunk.index)
        return f"mapped-{chunk.index}"

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        return "|".join(summaries)

    chunks = [
        make_chunk(0),
        make_chunk(1),
        make_chunk(2),
        make_chunk(3),
    ]

    result = MapReduceStrategy(
        map_fn=map_fn,
        reduce_fn=reduce_fn,
    ).summarize(chunks)

    assert calls == [0, 1, 2, 3]

    assert [item.chunk_index for item in result.map_results] == [0, 1, 2, 3]

    assert result.source_chunk_indexes == (
        0,
        1,
        2,
        3,
    )


def test_reduce_receives_map_results_in_source_order():
    received: list[tuple[str, ...]] = []

    def map_fn(chunk: Chunk) -> str:
        return f"summary-{chunk.index}"

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        received.append(tuple(summaries))
        return "final"

    chunks = [
        make_chunk(0),
        make_chunk(1),
        make_chunk(2),
    ]

    MapReduceStrategy(
        map_fn=map_fn,
        reduce_fn=reduce_fn,
    ).summarize(chunks)

    assert received == [
        (
            "summary-0",
            "summary-1",
            "summary-2",
        )
    ]


def test_map_result_preserves_chunk_token_count():
    def map_fn(chunk: Chunk) -> str:
        return "summary"

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        return summaries[0]

    chunk = make_chunk(
        0,
        "one two three four",
    )

    result = MapReduceStrategy(
        map_fn=map_fn,
        reduce_fn=reduce_fn,
    ).summarize([chunk])

    assert result.map_results[0].token_count == chunk.token_count


def test_map_failure_is_propagated():
    def map_fn(chunk: Chunk) -> str:
        raise RuntimeError(f"map failed for chunk {chunk.index}")

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        return "unused"

    with pytest.raises(
        RuntimeError,
        match="map failed for chunk 1",
    ):
        MapReduceStrategy(
            map_fn=map_fn,
            reduce_fn=reduce_fn,
        ).summarize([make_chunk(1)])


def test_reduce_failure_is_propagated():
    def map_fn(chunk: Chunk) -> str:
        return f"mapped-{chunk.index}"

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        raise RuntimeError("reduce failed")

    with pytest.raises(
        RuntimeError,
        match="reduce failed",
    ):
        MapReduceStrategy(
            map_fn=map_fn,
            reduce_fn=reduce_fn,
        ).summarize(
            [
                make_chunk(0),
                make_chunk(1),
            ]
        )


def test_map_function_must_return_string():
    def map_fn(chunk: Chunk) -> int:
        return 123

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        return "unused"

    with pytest.raises(
        TypeError,
        match="map_fn must return a string",
    ):
        MapReduceStrategy(
            map_fn=map_fn,
            reduce_fn=reduce_fn,
        ).summarize([make_chunk(0)])


def test_reduce_function_must_return_string():
    def map_fn(chunk: Chunk) -> str:
        return "mapped"

    def reduce_fn(summaries: tuple[str, ...]) -> int:
        return 123

    with pytest.raises(
        TypeError,
        match="reduce_fn must return a string",
    ):
        MapReduceStrategy(
            map_fn=map_fn,
            reduce_fn=reduce_fn,
        ).summarize([make_chunk(0)])


def test_map_function_must_be_callable():
    with pytest.raises(TypeError, match="map_fn"):
        MapReduceStrategy(
            map_fn=None,  # type: ignore[arg-type]
            reduce_fn=lambda _: "result",
        )


def test_reduce_function_must_be_callable():
    with pytest.raises(TypeError, match="reduce_fn"):
        MapReduceStrategy(
            map_fn=lambda _: "result",
            reduce_fn=None,  # type: ignore[arg-type]
        )


def test_map_reduce_is_deterministic():
    chunks = [
        make_chunk(0),
        make_chunk(1),
        make_chunk(2),
    ]

    def map_fn(chunk: Chunk) -> str:
        return f"MAP:{chunk.text}"

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        return "REDUCE:" + "|".join(summaries)

    strategy = MapReduceStrategy(
        map_fn=map_fn,
        reduce_fn=reduce_fn,
    )

    first = strategy.summarize(chunks)
    second = strategy.summarize(chunks)

    assert first == second


def test_empty_map_summary_is_preserved():
    def map_fn(chunk: Chunk) -> str:
        return ""

    def reduce_fn(summaries: tuple[str, ...]) -> str:
        return "|".join(summaries)

    result = MapReduceStrategy(
        map_fn=map_fn,
        reduce_fn=reduce_fn,
    ).summarize(
        [
            make_chunk(0),
            make_chunk(1),
        ]
    )

    assert [item.summary for item in result.map_results] == [
        "",
        "",
    ]

    assert result.summary == "|"
