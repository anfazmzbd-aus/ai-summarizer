from app.runtime.events.event_types import (
    ExecutionStarted,
    ExecutionFinished,
    LayerStarted,
    LayerFinished,
    NodeStarted,
    NodeFinished,
)


class TraceSubscriber:

    def __init__(self, trace):

        self.trace = trace

    def __call__(self, event):

        if isinstance(event, ExecutionStarted):
            self.trace.execution_started()

        elif isinstance(event, ExecutionFinished):
            self.trace.execution_finished()

        elif isinstance(event, LayerStarted):
            self.trace.layer_started(event.layer)

        elif isinstance(event, LayerFinished):
            self.trace.layer_finished(event.layer)

        elif isinstance(event, NodeStarted):
            self.trace.node_started(event.node)

        elif isinstance(event, NodeFinished):
            self.trace.node_finished(event.node)
