"""
Tests for the deterministic ContextAggregator.
"""

from __future__ import annotations

import pytest

from app.summarization.chunking.models import Chunk
from app.summarization.strategies.context.aggregator import (
    ContextAggregator,
)
from app.summarization.strategies.context.models import (
    AggregatedContext,
)
from app.summarization.strategies.models import MapResult


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


def make_result(
    index: int,
    summary: str | None = None,
) -> MapResult:
    return MapResult(
        chunk_index=index,
        summary=summary or f"summary-{index}",
        token_count=index + 1,
        metadata={
            "map_index": index,
        },
    )


def test_empty_input_returns_empty_context():
    result = ContextAggregator().aggregate([], [])

    assert isinstance(result, AggregatedContext)
    assert result.envelopes == ()
    assert result.source_chunk_indexes == ()
    assert result.total_tokens == 0
    assert result.total_characters == 0
    assert result.metadata["chunk_count"] == 0


def test_single_chunk_is_aggregated():
    chunk = make_chunk(0, "one two")
    map_result = make_result(0, "short summary")

    result = ContextAggregator().aggregate(
        [chunk],
        [map_result],
    )

    envelope = result.envelopes[0]

    assert envelope.chunk_index == 0
    assert envelope.summary == "short summary"
    assert envelope.source_text == "one two"
    assert envelope.start_offset == chunk.start_offset
    assert envelope.end_offset == chunk.end_offset
    assert envelope.token_count == chunk.token_count
    assert envelope.character_count == chunk.character_count
    assert envelope.preceding_chunk_index is None
    assert envelope.following_chunk_index is None


def test_multiple_chunks_preserve_order():
    chunks = [
        make_chunk(0),
        make_chunk(1),
        make_chunk(2),
    ]

    results = [
        make_result(0),
        make_result(1),
        make_result(2),
    ]

    result = ContextAggregator().aggregate(
        chunks,
        results,
    )

    assert result.source_chunk_indexes == (
        0,
        1,
        2,
    )

    assert [envelope.chunk_index for envelope in result.envelopes] == [0, 1, 2]


def test_adjacent_chunk_relationships_are_preserved():
    chunks = [
        make_chunk(0),
        make_chunk(1),
        make_chunk(2),
    ]

    results = [
        make_result(0),
        make_result(1),
        make_result(2),
    ]

    result = ContextAggregator().aggregate(
        chunks,
        results,
    )

    first, middle, last = result.envelopes

    assert first.preceding_chunk_index is None
    assert first.following_chunk_index == 1

    assert middle.preceding_chunk_index == 0
    assert middle.following_chunk_index == 2

    assert last.preceding_chunk_index == 1
    assert last.following_chunk_index is None


def test_source_offsets_are_preserved():
    chunks = [
        make_chunk(0, "first"),
        make_chunk(1, "second"),
    ]

    results = [
        make_result(0),
        make_result(1),
    ]

    result = ContextAggregator().aggregate(
        chunks,
        results,
    )

    assert result.start_offset == chunks[0].start_offset
    assert result.end_offset == chunks[-1].end_offset

    assert result.envelopes[0].start_offset == 0
    assert result.envelopes[1].start_offset == 10


def test_total_tokens_are_aggregated_from_chunks():
    chunks = [
        make_chunk(0, "one"),
        make_chunk(1, "one two"),
        make_chunk(2, "one two three"),
    ]

    results = [
        make_result(0),
        make_result(1),
        make_result(2),
    ]

    result = ContextAggregator().aggregate(
        chunks,
        results,
    )

    assert result.total_tokens == (
        chunks[0].token_count + chunks[1].token_count + chunks[2].token_count
    )


def test_total_characters_are_aggregated_from_chunks():
    chunks = [
        make_chunk(0, "abc"),
        make_chunk(1, "abcd"),
        make_chunk(2, "abcde"),
    ]

    results = [
        make_result(0),
        make_result(1),
        make_result(2),
    ]

    result = ContextAggregator().aggregate(
        chunks,
        results,
    )

    assert result.total_characters == (
        chunks[0].character_count
        + chunks[1].character_count
        + chunks[2].character_count
    )


def test_map_result_metadata_is_preserved():
    chunks = [make_chunk(0)]
    results = [make_result(0)]

    result = ContextAggregator().aggregate(
        chunks,
        results,
    )

    assert result.envelopes[0].metadata == {
        "map_index": 0,
    }


def test_mismatched_lengths_are_rejected():
    chunks = [
        make_chunk(0),
        make_chunk(1),
    ]

    results = [
        make_result(0),
    ]

    with pytest.raises(
        ValueError,
        match="equal lengths",
    ):
        ContextAggregator().aggregate(
            chunks,
            results,
        )


def test_provenance_mismatch_is_rejected():
    chunks = [
        make_chunk(0),
        make_chunk(1),
    ]

    results = [
        make_result(0),
        make_result(2),
    ]

    with pytest.raises(
        ValueError,
        match="provenance",
    ):
        ContextAggregator().aggregate(
            chunks,
            results,
        )


def test_duplicate_chunk_indexes_are_rejected():
    chunks = [
        make_chunk(0),
        make_chunk(0),
    ]

    results = [
        make_result(0),
        make_result(0),
    ]

    with pytest.raises(
        ValueError,
        match="duplicate",
    ):
        ContextAggregator().aggregate(
            chunks,
            results,
        )


def test_out_of_order_chunks_are_rejected():
    chunks = [
        make_chunk(1),
        make_chunk(0),
    ]

    results = [
        make_result(1),
        make_result(0),
    ]

    with pytest.raises(
        ValueError,
        match="source order",
    ):
        ContextAggregator().aggregate(
            chunks,
            results,
        )


def test_out_of_order_map_results_are_rejected():
    chunks = [
        make_chunk(0),
        make_chunk(1),
    ]

    results = [
        make_result(1),
        make_result(0),
    ]

    with pytest.raises(
        ValueError,
        match="source order",
    ):
        ContextAggregator().aggregate(
            chunks,
            results,
        )


def test_empty_chunks_with_results_are_rejected():
    with pytest.raises(
        ValueError,
        match="without chunks",
    ):
        ContextAggregator().aggregate(
            [],
            [make_result(0)],
        )


def test_aggregation_is_deterministic():
    chunks = [
        make_chunk(0, "alpha"),
        make_chunk(1, "beta"),
        make_chunk(2, "gamma"),
    ]

    results = [
        make_result(0, "A"),
        make_result(1, "B"),
        make_result(2, "C"),
    ]

    aggregator = ContextAggregator()

    first = aggregator.aggregate(
        chunks,
        results,
    )

    second = aggregator.aggregate(
        chunks,
        results,
    )

    assert first == second


def test_non_chunk_input_is_rejected():
    with pytest.raises(
        TypeError,
        match="Chunk instances",
    ):
        ContextAggregator().aggregate(
            ["not-a-chunk"],  # type: ignore[list-item]
            [make_result(0)],
        )


def test_non_map_result_input_is_rejected():
    with pytest.raises(
        TypeError,
        match="MapResult instances",
    ):
        ContextAggregator().aggregate(
            [make_chunk(0)],
            ["not-a-result"],  # type: ignore[list-item]
        )
