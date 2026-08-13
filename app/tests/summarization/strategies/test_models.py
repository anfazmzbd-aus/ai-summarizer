"""
Tests for V9.2 Map-Reduce strategy models.
"""

from __future__ import annotations

import pytest

from app.summarization.strategies.models import (
    MapReduceResult,
    MapResult,
    ReduceInput,
)


def make_map_result(
    index: int = 0,
    summary: str = "summary",
) -> MapResult:
    return MapResult(
        chunk_index=index,
        summary=summary,
        token_count=10,
    )


def test_map_result_defaults():
    result = make_map_result()

    assert result.chunk_index == 0
    assert result.summary == "summary"
    assert result.token_count == 10
    assert result.metadata == {}


def test_map_result_rejects_negative_chunk_index():
    with pytest.raises(ValueError, match="chunk_index"):
        MapResult(
            chunk_index=-1,
            summary="summary",
        )


def test_map_result_rejects_negative_token_count():
    with pytest.raises(ValueError, match="token_count"):
        MapResult(
            chunk_index=0,
            summary="summary",
            token_count=-1,
        )


def test_map_result_rejects_non_string_summary():
    with pytest.raises(TypeError, match="summary"):
        MapResult(
            chunk_index=0,
            summary=123,  # type: ignore[arg-type]
        )


def test_reduce_input_preserves_result_order():
    results = (
        make_map_result(0),
        make_map_result(1),
        make_map_result(2),
    )

    reduce_input = ReduceInput(
        results=results,
        source_chunk_indexes=(0, 1, 2),
    )

    assert reduce_input.results == results
    assert reduce_input.source_chunk_indexes == (0, 1, 2)


def test_reduce_input_rejects_mismatched_lengths():
    results = (
        make_map_result(0),
        make_map_result(1),
    )

    with pytest.raises(
        ValueError,
        match="equal lengths",
    ):
        ReduceInput(
            results=results,
            source_chunk_indexes=(0,),
        )


def test_reduce_input_rejects_wrong_provenance():
    results = (
        make_map_result(0),
        make_map_result(1),
    )

    with pytest.raises(
        ValueError,
        match="ordered MAP results",
    ):
        ReduceInput(
            results=results,
            source_chunk_indexes=(1, 0),
        )


def test_map_reduce_result_preserves_provenance():
    results = (
        make_map_result(0),
        make_map_result(1),
    )

    result = MapReduceResult(
        summary="final summary",
        map_results=results,
        source_chunk_indexes=(0, 1),
    )

    assert result.summary == "final summary"
    assert result.map_results == results
    assert result.source_chunk_indexes == (0, 1)


def test_map_reduce_result_rejects_wrong_provenance():
    results = (
        make_map_result(0),
        make_map_result(1),
    )

    with pytest.raises(
        ValueError,
        match="ordered MAP results",
    ):
        MapReduceResult(
            summary="final",
            map_results=results,
            source_chunk_indexes=(1, 0),
        )


def test_empty_map_reduce_result_is_valid():
    result = MapReduceResult(
        summary="",
        map_results=(),
        source_chunk_indexes=(),
    )

    assert result.summary == ""
    assert result.map_results == ()
    assert result.source_chunk_indexes == ()
