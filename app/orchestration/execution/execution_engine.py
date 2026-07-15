from dataclasses import dataclass

from app.orchestration.graph.graph_validator import (
    GraphValidator,
)

from app.orchestration.execution.layer_executor import (
    LayerExecutor,
)


@dataclass
class ExecutionResult:

    state: object

    outputs: dict


class ExecutionEngine:

    def __init__(self, registry, contracts):

        self.validator = GraphValidator()  # FIX
        self.layer_executor = LayerExecutor(registry, contracts)

    def execute(self, graph, initial_state):

        self.validator.validate(graph)

        state = initial_state
        # print(f"state: {state}")
        # print(f"graph: {graph}")

        for layer in graph.layers:
            self.layer_executor.execute_layer(layer, state)

        # print(f"state: {state}")
        # print(f"outputs: {state.artifacts}")

        return ExecutionResult(
            state=state,
            outputs=state.artifacts,
        )
