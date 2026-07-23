from unittest.mock import Mock

from app.runtime.events.event_bus import EventBus
from app.runtime.events.event_types import (
    ExecutionStarted,
)


def test_subscriber_receives_event():

    bus = EventBus()

    subscriber = Mock()

    bus.subscribe(
        ExecutionStarted,
        subscriber,
    )

    event = ExecutionStarted(
        execution_id="exec-001",
    )

    bus.publish(event)

    subscriber.assert_called_once_with(event)


def test_multiple_subscribers_receive_event():

    bus = EventBus()

    subscriber1 = Mock()
    subscriber2 = Mock()

    bus.subscribe(
        ExecutionStarted,
        subscriber1,
    )

    bus.subscribe(
        ExecutionStarted,
        subscriber2,
    )

    event = ExecutionStarted(
        execution_id="exec-001",
    )

    bus.publish(event)

    subscriber1.assert_called_once_with(event)
    subscriber2.assert_called_once_with(event)


def test_unsubscribe():

    bus = EventBus()

    subscriber = Mock()

    bus.subscribe(
        ExecutionStarted,
        subscriber,
    )

    bus.unsubscribe(
        ExecutionStarted,
        subscriber,
    )

    bus.publish(
        ExecutionStarted(
            execution_id="exec-001",
        )
    )

    subscriber.assert_not_called()
