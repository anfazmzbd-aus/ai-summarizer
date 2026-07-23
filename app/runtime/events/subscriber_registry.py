from app.runtime.events.event_types import (
    ExecutionStarted,
    ExecutionFinished,
    LayerStarted,
    LayerFinished,
    NodeStarted,
    NodeFinished,
    NodeFailed,
    RetryFinished,
)

from .logging_subscriber import LoggingSubscriber
from .metrics_subscriber import MetricsSubscriber
from .trace_subscriber import TraceSubscriber


class SubscriberRegistry:

    def register_defaults(
        self,
        bus,
        trace,
        metrics,
        logger,
    ):

        trace_subscriber = TraceSubscriber(trace)

        metrics_subscriber = MetricsSubscriber(metrics)

        logging_subscriber = LoggingSubscriber(logger)

        events = [
            ExecutionStarted,
            ExecutionFinished,
            LayerStarted,
            LayerFinished,
            NodeStarted,
            NodeFinished,
            NodeFailed,
            RetryFinished,
        ]

        for event in events:

            bus.subscribe(
                event,
                trace_subscriber,
            )

            bus.subscribe(
                event,
                metrics_subscriber,
            )

            bus.subscribe(
                event,
                logging_subscriber,
            )
