"""
Tests for streaming models.
"""

from __future__ import annotations

import pytest

from app.summarization.streaming.models import (
    StreamEventType,
    StreamResult,
)


def test_stream_event_types_are_stable():
    assert StreamEventType.STARTED.value == "started"
    assert StreamEventType.CHUNK.value == "chunk"
    assert StreamEventType.COMPLETED.value == "completed"
    assert StreamEventType.ERROR.value == "error"


def test_stream_result_defaults():
    result = StreamResult(
        content="hello",
        chunk_count=1,
    )

    assert result.content == "hello"
    assert result.chunk_count == 1
    assert result.metadata == {}


def test_stream_result_preserves_metadata():
    result = StreamResult(
        content="hello",
        chunk_count=2,
        metadata={"source": "test"},
    )

    assert result.metadata == {"source": "test"}


def test_stream_result_rejects_negative_chunk_count():
    with pytest.raises(
        ValueError,
        match="chunk_count",
    ):
        StreamResult(
            content="hello",
            chunk_count=-1,
        )


def test_stream_result_rejects_non_string_content():
    with pytest.raises(
        TypeError,
        match="content",
    ):
        StreamResult(
            content=123,  # type: ignore[arg-type]
            chunk_count=1,
        )
