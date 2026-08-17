"""
Tests for V9.3-M9 intelligent streaming integration.
"""

from __future__ import annotations

import pytest

from app.summarization.streaming import (
    IntelligentStreamContext,
    IntelligentSummarizationStreamer,
    StreamChunkEvent,
    StreamCompletedEvent,
    StreamErrorEvent,
    StreamStartedEvent,
)


def make_context() -> IntelligentStreamContext:
    return IntelligentStreamContext(
        planner={
            "planner_version": "v9.3-m1",
            "strategy": "map_reduce",
        },
        document={
            "document_type": "technical",
            "chunk_count": 4,
        },
        intent={
            "intent": "technical",
        },
        adaptive={
            "strategy": "map_reduce",
            "promoted": True,
        },
        optimization={
            "token_budget": 4096,
            "estimated_latency_ms": 800,
        },
        quality={
            "score": 0.82,
            "passed": True,
        },
        resilience={
            "fallback_used": False,
        },
    )


def test_context_is_immutable():
    context = make_context()

    with pytest.raises(
        AttributeError,
    ):
        context.planner = {}  # type: ignore[misc]


def test_context_rejects_invalid_planner():
    with pytest.raises(
        TypeError,
        match="planner",
    ):
        IntelligentStreamContext(
            planner="invalid",  # type: ignore[arg-type]
        )


def test_context_rejects_invalid_document():
    with pytest.raises(
        TypeError,
        match="document",
    ):
        IntelligentStreamContext(
            document="invalid",  # type: ignore[arg-type]
        )


def test_context_rejects_invalid_intent():
    with pytest.raises(
        TypeError,
        match="intent",
    ):
        IntelligentStreamContext(
            intent="invalid",  # type: ignore[arg-type]
        )


def test_context_rejects_invalid_adaptive():
    with pytest.raises(
        TypeError,
        match="adaptive",
    ):
        IntelligentStreamContext(
            adaptive="invalid",  # type: ignore[arg-type]
        )


def test_context_rejects_invalid_optimization():
    with pytest.raises(
        TypeError,
        match="optimization",
    ):
        IntelligentStreamContext(
            optimization="invalid",  # type: ignore[arg-type]
        )


def test_context_rejects_invalid_quality():
    with pytest.raises(
        TypeError,
        match="quality",
    ):
        IntelligentStreamContext(
            quality="invalid",  # type: ignore[arg-type]
        )


def test_context_rejects_invalid_resilience():
    with pytest.raises(
        TypeError,
        match="resilience",
    ):
        IntelligentStreamContext(
            resilience="invalid",  # type: ignore[arg-type]
        )


def test_context_metadata_is_namespaced():
    metadata = make_context().to_metadata()

    assert "intelligence" in metadata

    intelligence = metadata["intelligence"]

    assert intelligence["planner"]["planner_version"] == "v9.3-m1"
    assert intelligence["document"]["chunk_count"] == 4
    assert intelligence["intent"]["intent"] == "technical"
    assert intelligence["adaptive"]["promoted"] is True
    assert intelligence["optimization"]["token_budget"] == 4096
    assert intelligence["quality"]["score"] == 0.82
    assert intelligence["resilience"]["fallback_used"] is False


def test_intelligent_stream_preserves_event_order():
    events = list(
        IntelligentSummarizationStreamer().stream(
            ["hello", " ", "world"],
            context=make_context(),
        )
    )

    assert isinstance(
        events[0],
        StreamStartedEvent,
    )

    assert isinstance(
        events[1],
        StreamChunkEvent,
    )

    assert isinstance(
        events[2],
        StreamChunkEvent,
    )

    assert isinstance(
        events[3],
        StreamChunkEvent,
    )

    assert isinstance(
        events[4],
        StreamCompletedEvent,
    )


def test_intelligent_stream_preserves_chunk_sequence():
    events = list(
        IntelligentSummarizationStreamer().stream(
            ["a", "b", "c"],
            context=make_context(),
        )
    )

    chunks = [
        event
        for event in events
        if isinstance(
            event,
            StreamChunkEvent,
        )
    ]

    assert [event.sequence for event in chunks] == [0, 1, 2]


def test_intelligence_metadata_is_present_on_started_event():
    events = list(
        IntelligentSummarizationStreamer().stream(
            ["hello"],
            context=make_context(),
        )
    )

    started = events[0]

    assert isinstance(
        started,
        StreamStartedEvent,
    )

    intelligence = started.metadata["intelligence"]

    assert intelligence["planner"]["planner_version"] == "v9.3-m1"


def test_intelligence_metadata_is_present_on_chunks():
    events = list(
        IntelligentSummarizationStreamer().stream(
            ["a", "b"],
            context=make_context(),
        )
    )

    chunks = [
        event
        for event in events
        if isinstance(
            event,
            StreamChunkEvent,
        )
    ]

    for chunk in chunks:
        assert "intelligence" in chunk.metadata

    assert chunks[0].metadata["intelligence"]["intent"]["intent"] == "technical"


def test_intelligence_metadata_is_present_on_completion():
    events = list(
        IntelligentSummarizationStreamer().stream(
            ["hello"],
            context=make_context(),
        )
    )

    completed = events[-1]

    assert isinstance(
        completed,
        StreamCompletedEvent,
    )

    assert completed.metadata["intelligence"]["quality"]["passed"] is True


def test_streaming_version_is_present():
    events = list(
        IntelligentSummarizationStreamer().stream(
            ["hello"],
        )
    )

    for event in events:
        assert event.metadata["streaming"]["streamer_version"] == "v9.3-m9"

        assert event.metadata["streaming"]["intelligent"] is True


def test_explicit_metadata_is_preserved():
    events = list(
        IntelligentSummarizationStreamer().stream(
            ["hello"],
            metadata={
                "execution_id": "exec-123",
                "strategy": "direct",
            },
        )
    )

    for event in events:
        assert event.metadata["execution_id"] == "exec-123"

        assert event.metadata["strategy"] == "direct"


def test_explicit_metadata_and_intelligence_are_combined():
    events = list(
        IntelligentSummarizationStreamer().stream(
            ["hello"],
            context=make_context(),
            metadata={
                "execution_id": "exec-123",
            },
        )
    )

    started = events[0]

    assert isinstance(
        started,
        StreamStartedEvent,
    )

    assert started.metadata["execution_id"] == "exec-123"

    assert started.metadata["intelligence"]["intent"]["intent"] == "technical"


def test_collect_preserves_content():
    result = IntelligentSummarizationStreamer().collect(
        ["hello", " ", "world"],
        context=make_context(),
    )

    assert result.content == "hello world"
    assert result.chunk_count == 3


def test_collect_preserves_intelligence_metadata():
    result = IntelligentSummarizationStreamer().collect(
        ["hello"],
        context=make_context(),
    )

    assert result.metadata["intelligence"]["planner"]["planner_version"] == "v9.3-m1"


def test_collect_preserves_streaming_metadata():
    result = IntelligentSummarizationStreamer().collect(
        ["hello"],
    )

    assert result.metadata["streaming"]["streamer_version"] == "v9.3-m9"


def test_stream_error_preserves_intelligence_metadata():
    events = list(
        IntelligentSummarizationStreamer().stream(
            ["valid", 123],  # type: ignore[list-item]
            context=make_context(),
        )
    )

    error = events[-1]

    assert isinstance(
        error,
        StreamErrorEvent,
    )

    assert error.metadata["intelligence"]["resilience"]["fallback_used"] is False


def test_stream_error_preserves_error_sequence():
    def failing_source():
        yield "valid"
        raise RuntimeError("source failed")

    events = list(
        IntelligentSummarizationStreamer().stream(
            failing_source(),
            context=make_context(),
        )
    )

    error = events[-1]

    assert isinstance(
        error,
        StreamErrorEvent,
    )

    assert error.sequence == 1
    assert error.error_type == "RuntimeError"
    assert error.message == "source failed"


def test_empty_stream_remains_compatible():
    events = list(
        IntelligentSummarizationStreamer().stream(
            [],
            context=make_context(),
        )
    )

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


def test_stream_is_deterministic():
    source = [
        "alpha",
        "beta",
        "gamma",
    ]

    first = list(
        IntelligentSummarizationStreamer().stream(
            source,
            context=make_context(),
        )
    )

    second = list(
        IntelligentSummarizationStreamer().stream(
            source,
            context=make_context(),
        )
    )

    assert first == second


def test_context_metadata_is_snapshot_based():
    planner_metadata = {
        "planner_version": "v9.3-m1",
    }

    context = IntelligentStreamContext(
        planner=planner_metadata,
    )

    metadata = context.to_metadata()

    planner_metadata["planner_version"] = "changed"

    assert metadata["intelligence"]["planner"]["planner_version"] == "v9.3-m1"


def test_no_provider_dependency():
    streamer = IntelligentSummarizationStreamer()

    events = list(
        streamer.stream(
            ["provider independent"],
            context=IntelligentStreamContext(
                planner={
                    "planner_version": "v9.3-m1",
                },
            ),
        )
    )

    assert len(events) == 3


def test_invalid_metadata_is_rejected():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        list(
            IntelligentSummarizationStreamer().stream(
                ["hello"],
                metadata="invalid",  # type: ignore[arg-type]
            )
        )


def test_invalid_context_is_rejected():
    with pytest.raises(
        TypeError,
        match="context",
    ):
        list(
            IntelligentSummarizationStreamer().stream(
                ["hello"],
                context="invalid",  # type: ignore[arg-type]
            )
        )


def test_existing_streamer_can_be_injected():
    from app.summarization.streaming import (
        SummarizationStreamer,
    )

    base_streamer = SummarizationStreamer()

    streamer = IntelligentSummarizationStreamer(
        streamer=base_streamer,
    )

    result = streamer.collect(
        ["a", "b"],
    )

    assert result.content == "ab"
    assert result.chunk_count == 2
