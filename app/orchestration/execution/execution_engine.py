from dataclasses import dataclass

from app.orchestration.execution.node_executor import NodeExecutor
from app.orchestration.execution.layer_executor import LayerExecutor
from app.orchestration.graph.graph_validator import GraphValidator
from app.runtime.runtime_config import RuntimeConfig


@dataclass
class ExecutionResult:

    state: object

    outputs: dict


class ExecutionEngine:

    def __init__(
        self,
        registry,
        contracts,
        events=None,
    ):

        self.events = events

        self.validator = GraphValidator()

        config = RuntimeConfig()

        self.node_executor = NodeExecutor(
            registry,
            contracts,
            events,
        )

        self.layer_executor = LayerExecutor(
            node_executor=self.node_executor,
            runtime_config=config,
            events=events,
        )

    def _execution_started(self):

        if not self.events:
            return

        if hasattr(
            self.events,
            "execution_started",
        ):
            self.events.execution_started()

        else:
            from app.runtime.events.event_types import ExecutionStarted

            self.events.publish(
                ExecutionStarted(
                    execution_id="runtime",
                )
            )

    def _execution_finished(self):

        if not self.events:
            return

        if hasattr(
            self.events,
            "execution_finished",
        ):
            self.events.execution_finished()

        else:
            from app.runtime.events.event_types import ExecutionFinished

            self.events.publish(
                ExecutionFinished(
                    execution_id="runtime",
                )
            )

    def execute(
        self,
        graph,
        initial_state,
    ):

        self.validator.validate(graph)

        if self.events:
            self._execution_started()

        state = initial_state

        for layer in graph.layers:

            self.layer_executor.execute_layer(
                layer,
                state,
            )

        if self.events:
            self._execution_finished()

        return ExecutionResult(
            state=state,
            outputs=state.artifacts,
        )
