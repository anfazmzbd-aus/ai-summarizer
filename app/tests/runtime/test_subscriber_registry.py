from unittest.mock import Mock

from app.runtime.events.event_bus import EventBus
from app.runtime.events.subscriber_registry import SubscriberRegistry


def test_register_defaults_registers_subscribers():

    bus = Mock(spec=EventBus)

    registry = SubscriberRegistry()

    trace = Mock()
    metrics = Mock()
    logger = Mock()

    registry.register_defaults(
        bus=bus,
        trace=trace,
        metrics=metrics,
        logger=logger,
    )

    assert bus.subscribe.call_count > 0
