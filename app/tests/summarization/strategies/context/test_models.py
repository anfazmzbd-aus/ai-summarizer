"""
Tests for context aggregation models.
"""

from __future__ import annotations

import pytest

from app.summarization.strategies.context.models import (
    AggregatedContext,
    ContextEnvelope,
)

# from app.summarization.strategies.models import MapResult


def make_envelope(
    index: int = 0,
    summary: str = "summary",
) -> ContextEnvelope:
    return ContextEnvelope(
        chunk_index=index,
        summary=summary,
        source_text=f"text-{index}",
        start_offset=index * 100,
        end_offset=(index * 100) + 10,
        token_count=5,
        character_count=10,
    )


def test_context_envelope_defaults():
    envelope = make_envelope()

    assert envelope.chunk_index == 0
    assert envelope.summary == "summary"
    assert envelope.source_text == "text-0"
    assert envelope.start_offset == 0
    assert envelope.end_offset == 10
    assert envelope.token_count == 5
    assert envelope.character_count == 10
    assert envelope.preceding_chunk_index is None
    assert envelope.following_chunk_index is None
    assert envelope.metadata == {}


def test_context_envelope_preserves_relationships():
    envelope = ContextEnvelope(
        chunk_index=2,
        summary="summary",
        source_text="text",
        start_offset=20,
        end_offset=30,
        token_count=5,
        character_count=4,
        preceding_chunk_index=1,
        following_chunk_index=3,
    )

    assert envelope.preceding_chunk_index == 1
    assert envelope.following_chunk_index == 3


def test_context_envelope_rejects_negative_index():
    with pytest.raises(ValueError, match="chunk_index"):
        make_envelope(-1)


def test_context_envelope_rejects_invalid_offsets():
    with pytest.raises(
        ValueError,
        match="end_offset",
    ):
        ContextEnvelope(
            chunk_index=0,
            summary="summary",
            source_text="text",
            start_offset=20,
            end_offset=10,
            token_count=1,
            character_count=4,
        )


def test_context_envelope_rejects_negative_token_count():
    with pytest.raises(
        ValueError,
        match="token_count",
    ):
        ContextEnvelope(
            chunk_index=0,
            summary="summary",
            source_text="text",
            start_offset=0,
            end_offset=4,
            token_count=-1,
            character_count=4,
        )


def test_context_envelope_rejects_negative_character_count():
    with pytest.raises(
        ValueError,
        match="character_count",
    ):
        ContextEnvelope(
            chunk_index=0,
            summary="summary",
            source_text="text",
            start_offset=0,
            end_offset=4,
            token_count=1,
            character_count=-1,
        )


def test_aggregated_context_preserves_order():
    envelopes = (
        make_envelope(0),
        make_envelope(1),
    )

    result = AggregatedContext(
        envelopes=envelopes,
        source_chunk_indexes=(0, 1),
        start_offset=0,
        end_offset=110,
        total_tokens=10,
        total_characters=20,
    )

    assert result.envelopes == envelopes
    assert result.source_chunk_indexes == (0, 1)


def test_aggregated_context_rejects_wrong_provenance():
    envelopes = (
        make_envelope(0),
        make_envelope(1),
    )

    with pytest.raises(
        ValueError,
        match="envelope order",
    ):
        AggregatedContext(
            envelopes=envelopes,
            source_chunk_indexes=(1, 0),
            start_offset=0,
            end_offset=110,
            total_tokens=10,
            total_characters=20,
        )


def test_aggregated_context_empty():
    result = AggregatedContext.empty()

    assert result.envelopes == ()
    assert result.source_chunk_indexes == ()
    assert result.start_offset == 0
    assert result.end_offset == 0
    assert result.total_tokens == 0
    assert result.total_characters == 0
    assert result.metadata["chunk_count"] == 0


def test_context_envelope_metadata_is_preserved():
    metadata = {
        "strategy": "map_reduce",
        "source": "test",
    }

    envelope = ContextEnvelope(
        chunk_index=0,
        summary="summary",
        source_text="text",
        start_offset=0,
        end_offset=4,
        token_count=1,
        character_count=4,
        metadata=metadata,
    )

    assert envelope.metadata == metadata
