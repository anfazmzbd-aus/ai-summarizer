from dataclasses import dataclass

from app.orchestration.graph.graph_validator import (
    GraphValidator,
)

from app.orchestration.execution.layer_executor import (
    LayerExecutor,
)

from app.orchestration.state.state_merger import (
    StateMerger,
)


@dataclass
class ExecutionResult:

    state: object

    outputs: dict


class ExecutionEngine:

    def __init__(
        self,
        registry,
        contracts,
    ):

        self.validator = (
            GraphValidator()
        )

        self.layer_executor = (
            LayerExecutor(

                registry,

                contracts,

            )
        )

        self.merger = (
            StateMerger()
        )

    def execute(

        self,

        graph,

        initial_state,

    ):

        self.validator.validate(
            graph
        )

        state = (
            initial_state
        )

        for layer in (
            graph.layers
        ):

            batch = (

                self.layer_executor
                .execute_layer(

                    layer,

                    state,

                    graph,

                )

            )

            state = (

                self.merger
                .commit_batch(

                    state,

                    batch,

                    graph,

                )

            )

        return ExecutionResult(

            state=state,

            outputs=(
                state.node_outputs
            ),

        )