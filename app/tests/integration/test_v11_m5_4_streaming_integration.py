"""V11 M5.4 integration with the existing V9 streaming capability."""

from fastapi.testclient import TestClient

from app.main import app
from app.summarization.streaming.events import (
    StreamChunkEvent,
    StreamCompletedEvent,
    StreamStartedEvent,
)
from app.summarization.streaming.streamer import SummarizationStreamer


def test_canonical_summary_can_be_streamed_through_v9_streamer() -> None:
    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": (
                "Artificial intelligence helps teams automate repetitive "
                "tasks and summarize operational information."
            ),
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    summary = payload["summary"]

    fragments = [
        summary[: len(summary) // 2],
        summary[len(summary) // 2 :],
    ]

    events = list(
        SummarizationStreamer().stream(
            fragments,
            metadata={
                "strategy": payload["metadata"]["strategy"],
                "chunk_count": payload["metadata"]["chunk_count"],
                "intelligence_mode": payload["metadata"]["intelligence_mode"],
            },
        )
    )

    assert isinstance(events[0], StreamStartedEvent)
    assert isinstance(events[1], StreamChunkEvent)
    assert isinstance(events[2], StreamChunkEvent)
    assert isinstance(events[3], StreamCompletedEvent)

    assert events[1].sequence == 0
    assert events[2].sequence == 1

    completed = events[3]

    assert completed.content == summary
    assert completed.chunk_count == 2

    assert completed.metadata["strategy"] == "direct"
    assert completed.metadata["chunk_count"] == 1
    assert completed.metadata["intelligence_mode"] == "preserve"


def test_streaming_preserves_metadata_and_reports_fragment_error() -> None:
    metadata = {
        "strategy": "map_reduce",
        "chunk_count": 8,
        "intelligence_mode": "preserve",
    }

    events = list(
        SummarizationStreamer().stream(
            ["valid fragment", 123],  # type: ignore[list-item]
            metadata=metadata,
        )
    )

    assert isinstance(events[0], StreamStartedEvent)
    assert isinstance(events[1], StreamChunkEvent)

    error = events[2]

    from app.summarization.streaming.events import StreamErrorEvent

    assert isinstance(error, StreamErrorEvent)

    assert error.error_type == "TypeError"
    assert error.sequence == 1
    assert "strings" in error.message

    assert error.metadata["strategy"] == "map_reduce"
    assert error.metadata["chunk_count"] == 8
    assert error.metadata["intelligence_mode"] == "preserve"

    assert not any(isinstance(event, StreamCompletedEvent) for event in events)
