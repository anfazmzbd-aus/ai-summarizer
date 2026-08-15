"""
Tests for the deterministic summarization streamer.
"""

from __future__ import annotations

import pytest

from app.summarization.streaming.events import (
    StreamChunkEvent,
    StreamCompletedEvent,
    StreamErrorEvent,
    StreamStartedEvent,
)
from app.summarization.streaming.streamer import (
    SummarizationStreamer,
)


def test_empty_stream_has_started_and_completed():
    events = list(SummarizationStreamer().stream([]))

    assert len(events) == 2

    assert isinstance(
        events[0],
        StreamStartedEvent,
    )

    assert isinstance(
        events[1],
        StreamCompletedEvent,
    )

    assert events[1].content == ""
    assert events[1].chunk_count == 0


def test_single_fragment_stream():
    events = list(
        SummarizationStreamer().stream(
            ["hello"],
        )
    )

    assert len(events) == 3

    assert isinstance(events[0], StreamStartedEvent)
    assert isinstance(events[1], StreamChunkEvent)
    assert isinstance(events[2], StreamCompletedEvent)

    chunk = events[1]
    completed = events[2]

    assert chunk.sequence == 0
    assert chunk.content == "hello"
    assert completed.content == "hello"
    assert completed.chunk_count == 1


def test_multiple_fragments_preserve_order():
    events = list(
        SummarizationStreamer().stream(
            [
                "Hello",
                " ",
                "world",
                "!",
            ]
        )
    )

    chunks = [event for event in events if isinstance(event, StreamChunkEvent)]

    assert [event.sequence for event in chunks] == [
        0,
        1,
        2,
        3,
    ]

    assert [event.content for event in chunks] == [
        "Hello",
        " ",
        "world",
        "!",
    ]


def test_stream_reconstructs_original_content():
    source = [
        "The ",
        "company ",
        "grew ",
        "rapidly.",
    ]

    events = list(SummarizationStreamer().stream(source))

    chunks = [event.content for event in events if isinstance(event, StreamChunkEvent)]

    completed = events[-1]

    assert "".join(chunks) == "".join(source)
    assert isinstance(completed, StreamCompletedEvent)
    assert completed.content == "The company grew rapidly."


def test_stream_metadata_is_preserved():
    metadata = {
        "execution_id": "exec-1",
        "strategy": "map_reduce",
    }

    events = list(
        SummarizationStreamer().stream(
            ["hello"],
            metadata=metadata,
        )
    )

    for event in events:
        assert event.metadata["execution_id"] == "exec-1"
        assert event.metadata["strategy"] == "map_reduce"


def test_chunk_metadata_contains_sequence():
    events = list(
        SummarizationStreamer().stream(
            ["a", "b"],
        )
    )

    chunks = [event for event in events if isinstance(event, StreamChunkEvent)]

    assert chunks[0].metadata["sequence"] == 0
    assert chunks[1].metadata["sequence"] == 1


def test_generator_source_is_supported():
    def source():
        yield "a"
        yield "b"
        yield "c"

    result = SummarizationStreamer().collect(source())

    assert result.content == "abc"
    assert result.chunk_count == 3


def test_tuple_source_is_supported():
    result = SummarizationStreamer().collect(
        ("a", "b"),
    )

    assert result.content == "ab"
    assert result.chunk_count == 2


def test_stream_error_is_emitted_for_invalid_fragment():
    events = list(
        SummarizationStreamer().stream(
            ["valid", 123],  # type: ignore[list-item]
        )
    )

    assert isinstance(events[0], StreamStartedEvent)
    assert isinstance(events[1], StreamChunkEvent)
    assert isinstance(events[2], StreamErrorEvent)

    error = events[2]

    assert error.error_type == "TypeError"
    assert "strings" in error.message
    assert error.sequence == 1


def test_error_stream_does_not_emit_completed():
    events = list(
        SummarizationStreamer().stream(
            ["valid", 123],  # type: ignore[list-item]
        )
    )

    assert not any(isinstance(event, StreamCompletedEvent) for event in events)


def test_error_event_uses_next_sequence_number():
    def failing_source():
        yield "a"
        raise RuntimeError("source failed")

    events = list(SummarizationStreamer().stream(failing_source()))

    chunks = [event for event in events if isinstance(event, StreamChunkEvent)]

    error = events[-1]

    assert [chunk.sequence for chunk in chunks] == [0]

    assert isinstance(error, StreamErrorEvent)
    assert error.sequence == 1
    assert error.message == "source failed"


def test_collect_reconstructs_stream():
    result = SummarizationStreamer().collect(
        [
            "one",
            " ",
            "two",
        ]
    )

    assert result.content == "one two"
    assert result.chunk_count == 3


def test_collect_raises_on_stream_error():
    def failing_source():
        yield "valid"
        raise RuntimeError("boom")

    with pytest.raises(
        RuntimeError,
        match="RuntimeError: boom",
    ):
        SummarizationStreamer().collect(failing_source())


def test_stream_is_deterministic():
    source = [
        "alpha",
        "beta",
        "gamma",
    ]

    first = list(SummarizationStreamer().stream(source))

    second = list(SummarizationStreamer().stream(source))

    assert first == second


def test_string_source_is_rejected():
    with pytest.raises(
        TypeError,
        match="not a string",
    ):
        list(SummarizationStreamer().stream("hello"))


def test_bytes_source_is_rejected():
    with pytest.raises(
        TypeError,
        match="not a string",
    ):
        list(SummarizationStreamer().stream(b"hello"))


def test_non_iterable_source_is_rejected():
    with pytest.raises(
        TypeError,
        match="iterable",
    ):
        list(SummarizationStreamer().stream(123))  # type: ignore[arg-type]


def test_stream_source_is_lazy():
    consumed = False

    def source():
        nonlocal consumed
        consumed = True
        yield "hello"

    iterator = SummarizationStreamer().stream(source())

    assert consumed is False

    next(iterator)

    assert consumed is False

    next(iterator)

    assert consumed is True
