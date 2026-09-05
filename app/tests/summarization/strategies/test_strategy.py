"""
Tests for advanced summarization strategies.
"""

from __future__ import annotations

from app.summarization.chunking.models import Chunk
from app.summarization.strategies.strategy import (
    DirectSummarizationStrategy,
    HierarchicalSummarizationStrategy,
    MapReduceSummarizationStrategy,
)


def make_chunk(
    index: int,
    text: str,
) -> Chunk:
    return Chunk(
        index=index,
        text=text,
        token_count=len(text.split()),
        character_count=len(text),
        start_offset=index * 10,
        end_offset=(index * 10) + len(text),
    )


def summarize(text: str) -> str:
    return f"[{text}]"


def test_direct_strategy_empty_input():
    result = DirectSummarizationStrategy().execute(
        [],
        summarize,
    )

    assert result.content == ""
    assert result.metadata["chunk_count"] == 0


def test_direct_strategy_combines_chunks():
    chunks = [
        make_chunk(0, "hello"),
        make_chunk(1, "world"),
    ]

    result = DirectSummarizationStrategy().execute(
        chunks,
        summarize,
    )

    assert result.content == "[helloworld]"
    assert result.metadata["chunk_count"] == 2


def test_direct_strategy_has_correct_type():
    chunks = [make_chunk(0, "hello")]

    result = DirectSummarizationStrategy().execute(
        chunks,
        summarize,
    )

    assert result.strategy.value == "direct"


def test_map_reduce_maps_chunks_in_order():
    calls: list[str] = []

    def recording_summarize(text: str) -> str:
        calls.append(text)
        return f"[{text}]"

    chunks = [
        make_chunk(0, "one"),
        make_chunk(1, "two"),
        make_chunk(2, "three"),
    ]

    result = MapReduceSummarizationStrategy().execute(
        chunks,
        recording_summarize,
    )

    assert calls[:3] == [
        "one",
        "two",
        "three",
    ]

    assert calls[3] == "[one]\n[two]\n[three]"
    assert result.strategy.value == "map_reduce"


def test_map_reduce_records_map_count():
    chunks = [
        make_chunk(0, "one"),
        make_chunk(1, "two"),
    ]

    result = MapReduceSummarizationStrategy().execute(
        chunks,
        summarize,
    )

    assert result.metadata["map_count"] == 2


def test_hierarchical_strategy_reduces_to_one_result():
    chunks = [
        make_chunk(0, "one"),
        make_chunk(1, "two"),
        make_chunk(2, "three"),
        make_chunk(3, "four"),
    ]

    result = HierarchicalSummarizationStrategy().execute(
        chunks,
        summarize,
    )

    assert result.strategy.value == "hierarchical"
    assert result.content
    assert result.metadata["chunk_count"] == 4


def test_hierarchical_strategy_empty_input():
    result = HierarchicalSummarizationStrategy().execute(
        [],
        summarize,
    )

    assert result.content == ""
    assert result.metadata["chunk_count"] == 0


def test_map_reduce_call_amplification_is_bounded_by_chunk_count():
    chunk_count = 128

    chunks = [make_chunk(index, f"chunk-{index}") for index in range(chunk_count)]

    calls: list[str] = []

    def recording_summarize(text: str) -> str:
        calls.append(text)
        return f"summary:{text}"

    result = MapReduceSummarizationStrategy().execute(
        chunks,
        recording_summarize,
    )

    assert result is not None

    assert len(calls) == chunk_count + 1

    assert calls[:chunk_count] == [chunk.text for chunk in chunks]

    reduce_input = calls[-1]

    for chunk in chunks:
        assert f"summary:{chunk.text}" in reduce_input


def test_hierarchical_call_amplification_is_bounded_by_chunk_count():
    chunk_count = 128

    chunks = [make_chunk(index, f"chunk-{index}") for index in range(chunk_count)]

    calls: list[str] = []

    def recording_summarize(text: str) -> str:
        calls.append(text)
        return f"summary:{text}"

    result = HierarchicalSummarizationStrategy().execute(
        chunks,
        recording_summarize,
    )

    assert result is not None
    assert result.strategy.value == "hierarchical"
    assert result.metadata["chunk_count"] == chunk_count

    expected_call_count = (2 * chunk_count) - 1

    assert len(calls) == expected_call_count

    assert calls[:chunk_count] == [chunk.text for chunk in chunks]


def test_repeated_large_hierarchical_execution_is_deterministic_and_stateless():
    chunk_count = 128

    chunks = [make_chunk(index, f"chunk-{index}") for index in range(chunk_count)]

    strategy = HierarchicalSummarizationStrategy()

    results = []
    call_counts = []

    for _ in range(5):
        calls: list[str] = []

        def recording_summarize(text: str) -> str:
            calls.append(text)
            return f"summary:{text}"

        result = strategy.execute(
            chunks,
            recording_summarize,
        )

        results.append(result)
        call_counts.append(len(calls))

    expected_call_count = (2 * chunk_count) - 1

    assert all(result == results[0] for result in results)

    assert call_counts == [expected_call_count] * 5
