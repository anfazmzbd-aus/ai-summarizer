from copy import deepcopy
from dataclasses import replace
from dataclasses import dataclass

from app.orchestration.state.state_model import (
    State,
    NodeOutputs,
)

from app.orchestration.graph.graph_schema import (
    GraphNode,
)


# -------------------------
# Commit Result
# -------------------------

@dataclass(
    frozen=True
)
class MergeResult:

    state: State

    committed_node: str


# -------------------------
# Merger
# -------------------------

class StateMerger:

    # ---------------------

    def commit(
        self,
        state: State,
        node: GraphNode,
        output: dict,
    ) -> MergeResult:

        self._validate_commit(
            state,
            node,
            output,
        )

        outputs = dict(
            state
            .node_outputs
            .values
        )

        outputs[
            node.name
        ] = deepcopy(
            output
        )

        new_state = replace(

            state,

            node_outputs=(
                NodeOutputs(
                    values=outputs
                )
            )
        )

        return MergeResult(

            state=new_state,

            committed_node=(
                node.name
            )
        )

    # ---------------------

    def commit_batch(
        self,
        state: State,
        layer,
        results,
        graph,
    ):

        next_state = state

        for node_name in sorted(
            results
        ):

            node = (
                graph
                .nodes[
                    node_name
                ]
            )

            result = (
                results[
                    node_name
                ]
            )

            merged = (
                self.commit(
                    next_state,
                    node,
                    result.output,
                )
            )

            next_state = (
                merged
                .state
            )

        return next_state

    # ---------------------

    def _validate_commit(
        self,
        state,
        node,
        output,
    ):

        if (
            node.name
            in
            state
            .node_outputs
            .values
        ):

            raise RuntimeError(

                f"{node.name}"

                " already committed"

            )

        if not isinstance(
            output,
            dict,
        ):

            raise TypeError(
                "Output must be dict"
            )