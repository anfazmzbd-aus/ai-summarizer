from dataclasses import dataclass
from time import monotonic

from app.orchestration.graph.graph_schema import (
    ExecutionGraph,
)

from app.orchestration.execution.execution_context import (
    ExecutionContext,
)

from app.orchestration.execution.layer_executor import (
    LayerExecutor,
)

from app.orchestration.state.state_model import (
    State,
)

from app.orchestration.state.state_merger import (
    StateMerger,
)

from app.orchestration.graph.graph_validator import (
    GraphValidator,
)


# -----------------------
# Result
# -----------------------

@dataclass(
    frozen=True
)
class ExecutionResult:

    state: State

    context: ExecutionContext


# -----------------------
# Engine
# -----------------------

class ExecutionEngine:

    def __init__(
        self,
        registry,
        contracts,
    ):

        self.validator = GraphValidator()

        self.layer_executor = LayerExecutor(
            registry=registry,
            contracts=contracts,
        )

        self.merger = (
            StateMerger()
        )

    # ---------------------

    def execute(
        self,
        graph: ExecutionGraph,
        initial_state: State,
    ) -> ExecutionResult:

        validation = (
            self.validator
            .validate(
                graph
            )
        )

        if not validation.valid:

            raise RuntimeError(
                validation.errors
            )

        state = (
            initial_state
        )

        context = (
            ExecutionContext(
                execution_id=(
                    graph.execution_id
                )
            )
        )

        for layer in graph.layers:

            state = (
                self._execute_layer(
                    graph=graph,
                    layer=layer,
                    state=state,
                    context=context,
                )
            )

        return ExecutionResult(

            state=state,

            context=context,
        )

    # ---------------------

    def _execute_layer(
        self,
        graph,
        layer,
        state,
        context,
    ):

        started = (
            monotonic()
        )

        results = (

            self.layer_executor
            .execute_batch(

                layer=layer,

                graph=graph,

                state=state,

                context=context,

            )

        )

        merged = (

            self.merger
            .commit_batch(

                state=state,

                results=results,

                graph=graph,

            )

        )

        duration = (
            (
                monotonic()
                -
                started
            )
            *
            1000
        )

        context.complete_layer(

            index=(
                layer.index
            ),

            duration_ms=(
                duration
            ),

            nodes=(
                layer.nodes
            ),

        )

        return merged