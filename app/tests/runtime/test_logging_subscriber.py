from unittest.mock import Mock

from app.runtime.events.event_types import ExecutionStarted
from app.runtime.events.logging_subscriber import LoggingSubscriber


def test_logging_subscriber_logs_event():

    logger = Mock()

    subscriber = LoggingSubscriber(logger)

    event = ExecutionStarted(
        execution_id="exec-001",
    )

    subscriber(event)

    logger.info.assert_called_once()
