from unittest.mock import Mock

from app.runtime.events.runtime_event_publisher import (
    RuntimeEventPublisher,
)

from app.runtime.events.event_types import (
    NodeStarted,
    LayerStarted,
    RetryFinished,
)


def test_execution_events():

    bus = Mock()

    publisher = RuntimeEventPublisher(
        bus,
        execution_id="exec-001",
    )

    publisher.execution_started()

    event = bus.publish.call_args.args[0]

    assert isinstance(
        event,
        type(event),
    )

    assert event.execution_id == "exec-001"


def test_node_events():

    bus = Mock()

    publisher = RuntimeEventPublisher(
        bus,
        execution_id="exec-001",
    )

    publisher.node_started("summary")

    event = bus.publish.call_args.args[0]

    assert isinstance(
        event,
        NodeStarted,
    )

    assert event.execution_id == "exec-001"
    assert event.node == "summary"


def test_layer_events():

    bus = Mock()

    publisher = RuntimeEventPublisher(
        bus,
        execution_id="exec-001",
    )

    publisher.layer_started(0)

    event = bus.publish.call_args.args[0]

    assert isinstance(
        event,
        LayerStarted,
    )

    assert event.layer_index == 0


def test_retry_event():

    bus = Mock()

    publisher = RuntimeEventPublisher(
        bus,
        execution_id="exec-001",
    )

    publisher.retry_finished(
        "summary",
        2,
    )

    event = bus.publish.call_args.args[0]

    assert isinstance(
        event,
        RetryFinished,
    )

    assert event.node == "summary"
    assert event.attempt == 2
