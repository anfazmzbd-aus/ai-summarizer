from unittest.mock import Mock

from app.runtime.events.event_types import ExecutionStarted
from app.runtime.events.trace_subscriber import TraceSubscriber


def test_execution_started_updates_trace():

    trace = Mock()

    subscriber = TraceSubscriber(trace)

    event = ExecutionStarted(
        execution_id="exec-001",
    )

    subscriber(event)

    trace.execution_started.assert_called_once()
