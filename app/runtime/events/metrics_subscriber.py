from app.runtime.events.event_types import (
    ExecutionStarted,
    ExecutionFinished,
    NodeFinished,
    NodeFailed,
    RetryFinished,
)


class MetricsSubscriber:

    def __init__(self, metrics):

        self.metrics = metrics

    def __call__(self, event):

        if isinstance(event, ExecutionStarted):
            self.metrics.execution_count += 1

        elif isinstance(event, NodeFinished):
            self.metrics.node_count += 1

        elif isinstance(event, RetryFinished):
            self.metrics.retry_count += 1

        elif isinstance(event, NodeFailed):
            self.metrics.failure_count += 1

        elif isinstance(event, ExecutionFinished):
            self.metrics.completed += 1
