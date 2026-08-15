"""
Tests for streaming lifecycle events.
"""

from __future__ import annotations

import pytest

from app.summarization.streaming.events import (
    StreamChunkEvent,
    StreamCompletedEvent,
    StreamErrorEvent,
    StreamStartedEvent,
)
from app.summarization.streaming.models import StreamEventType


def test_started_event_type():
    event = StreamStartedEvent()

    assert event.event_type is StreamEventType.STARTED


def test_started_event_metadata():
    event = StreamStartedEvent(
        metadata={"execution_id": "test-1"},
    )

    assert event.metadata == {
        "execution_id": "test-1",
    }


def test_chunk_event_type():
    event = StreamChunkEvent(
        sequence=0,
        content="hello",
    )

    assert event.event_type is StreamEventType.CHUNK


def test_chunk_event_preserves_sequence_and_content():
    event = StreamChunkEvent(
        sequence=4,
        content="hello",
        metadata={"source": "test"},
    )

    assert event.sequence == 4
    assert event.content == "hello"
    assert event.metadata == {"source": "test"}


def test_chunk_event_rejects_negative_sequence():
    with pytest.raises(
        ValueError,
        match="sequence",
    ):
        StreamChunkEvent(
            sequence=-1,
            content="hello",
        )


def test_chunk_event_rejects_non_string_content():
    with pytest.raises(
        TypeError,
        match="content",
    ):
        StreamChunkEvent(
            sequence=0,
            content=123,  # type: ignore[arg-type]
        )


def test_completed_event_type():
    event = StreamCompletedEvent(
        content="hello",
        chunk_count=1,
    )

    assert event.event_type is StreamEventType.COMPLETED


def test_completed_event_preserves_content():
    event = StreamCompletedEvent(
        content="hello world",
        chunk_count=2,
    )

    assert event.content == "hello world"
    assert event.chunk_count == 2


def test_completed_event_rejects_negative_count():
    with pytest.raises(
        ValueError,
        match="chunk_count",
    ):
        StreamCompletedEvent(
            content="hello",
            chunk_count=-1,
        )


def test_error_event_type():
    event = StreamErrorEvent(
        error_type="RuntimeError",
        message="failure",
        sequence=2,
    )

    assert event.event_type is StreamEventType.ERROR


def test_error_event_preserves_failure_information():
    event = StreamErrorEvent(
        error_type="RuntimeError",
        message="failure",
        sequence=2,
        metadata={"source": "test"},
    )

    assert event.error_type == "RuntimeError"
    assert event.message == "failure"
    assert event.sequence == 2
    assert event.metadata == {"source": "test"}


def test_error_event_rejects_empty_error_type():
    with pytest.raises(
        ValueError,
        match="error_type",
    ):
        StreamErrorEvent(
            error_type="",
            message="failure",
            sequence=0,
        )


def test_error_event_rejects_empty_message():
    with pytest.raises(
        ValueError,
        match="message",
    ):
        StreamErrorEvent(
            error_type="RuntimeError",
            message="",
            sequence=0,
        )
