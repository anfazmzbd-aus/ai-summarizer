from app.runtime.events.event_types import (
    ExecutionFinished,
    ExecutionStarted,
    LayerFinished,
    LayerStarted,
    NodeFailed,
    NodeFinished,
    NodeStarted,
    RetryFinished,
    RetryStarted,
)


def test_execution_started():

    event = ExecutionStarted(
        execution_id="abc",
    )

    assert event.execution_id == "abc"


def test_node_failed():

    event = NodeFailed(
        execution_id="abc",
        node="summary",
        error="failure",
    )

    assert event.node == "summary"
    assert event.error == "failure"


def test_retry_started():

    event = RetryStarted(
        execution_id="abc",
        node="summary",
        attempt=2,
    )

    assert event.attempt == 2


def test_all_events_construct():

    ExecutionFinished("id")
    LayerStarted("id", 0)
    LayerFinished("id", 0)
    NodeStarted("id", "summary")
    NodeFinished("id", "summary")
    RetryFinished("id", "summary", 2)
