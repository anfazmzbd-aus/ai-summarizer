from app.runtime.events.event_types import (
    ExecutionStarted,
    ExecutionFinished,
    LayerStarted,
    LayerFinished,
    NodeStarted,
    NodeFinished,
    NodeFailed,
    RetryStarted,
    RetryFinished,
)


class RuntimeEventPublisher:

    def __init__(
        self,
        bus,
        execution_id: str = "runtime",
    ):
        self._bus = bus
        self.execution_id = execution_id

    def execution_started(self):

        self._bus.publish(
            ExecutionStarted(
                execution_id=self.execution_id,
            )
        )

    def execution_finished(self):

        self._bus.publish(
            ExecutionFinished(
                execution_id=self.execution_id,
            )
        )

    def layer_started(
        self,
        layer_index: int,
    ):

        self._bus.publish(
            LayerStarted(
                execution_id=self.execution_id,
                layer_index=layer_index,
            )
        )

    def layer_finished(
        self,
        layer_index: int,
    ):

        self._bus.publish(
            LayerFinished(
                execution_id=self.execution_id,
                layer_index=layer_index,
            )
        )

    def node_started(
        self,
        node: str,
    ):

        self._bus.publish(
            NodeStarted(
                execution_id=self.execution_id,
                node=node,
            )
        )

    def node_finished(
        self,
        node: str,
    ):

        self._bus.publish(
            NodeFinished(
                execution_id=self.execution_id,
                node=node,
            )
        )

    def node_failed(
        self,
        node: str,
        error: str,
    ):

        self._bus.publish(
            NodeFailed(
                execution_id=self.execution_id,
                node=node,
                error=error,
            )
        )

    def retry_started(
        self,
        node: str,
        attempt: int,
    ):

        self._bus.publish(
            RetryStarted(
                execution_id=self.execution_id,
                node=node,
                attempt=attempt,
            )
        )

    def retry_finished(
        self,
        node: str,
        attempt: int,
    ):

        self._bus.publish(
            RetryFinished(
                execution_id=self.execution_id,
                node=node,
                attempt=attempt,
            )
        )
