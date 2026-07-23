from unittest.mock import Mock

from app.runtime.events.event_bus import EventBus
from app.runtime.events.event_dispatcher import EventDispatcher
from app.runtime.events.event_types import (
    ExecutionStarted,
)


def test_dispatch_calls_bus():

    bus = Mock(spec=EventBus)

    dispatcher = EventDispatcher(bus)

    event = ExecutionStarted(
        execution_id="exec-001",
    )

    dispatcher.dispatch(event)

    bus.publish.assert_called_once_with(event)
