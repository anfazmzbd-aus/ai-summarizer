from dataclasses import dataclass

from app.orchestration.execution.node_executor import NodeExecutor
from app.orchestration.graph.graph_validator import (
    GraphValidator,
)

from app.orchestration.execution.layer_executor import (
    LayerExecutor,
)
from app.runtime.runtime_config import RuntimeConfig


@dataclass
class ExecutionResult:

    state: object

    outputs: dict


class ExecutionEngine:

    def __init__(self, registry, contracts):

        self.validator = GraphValidator()  # FIX
        config = RuntimeConfig()
        self.node_executor = NodeExecutor(
            registry,
            contracts,
        )
        self.layer_executor = LayerExecutor(
            node_executor=self.node_executor,
            runtime_config=config,
        )

    def execute(self, graph, initial_state):

        self.validator.validate(graph)

        state = initial_state

        for layer in graph.layers:
            self.layer_executor.execute_layer(layer, state)

        return ExecutionResult(
            state=state,
            outputs=state.artifacts,
        )
