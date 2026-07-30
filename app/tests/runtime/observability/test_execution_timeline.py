from app.runtime.observability.execution_timeline import (
    ExecutionTimeline,
)


def test_timeline_initially_empty():
    timeline = ExecutionTimeline()

    assert timeline.events == []


def test_record_event():
    timeline = ExecutionTimeline()

    timeline.record(
        "execution_started",
        layer=1,
    )

    assert len(timeline.events) == 1

    event = timeline.events[0]

    assert event.event == "execution_started"

    assert event.details["layer"] == 1

    assert event.timestamp.tzinfo is not None


def test_record_multiple_events():
    timeline = ExecutionTimeline()

    timeline.record("created")

    timeline.record("scheduled")

    timeline.record("completed")

    assert len(timeline.events) == 3

    assert [e.event for e in timeline.events] == [
        "created",
        "scheduled",
        "completed",
    ]
