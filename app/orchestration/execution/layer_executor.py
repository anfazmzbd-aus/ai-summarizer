from app.orchestration.execution.node_executor import (
    NodeExecutor,
)


class LayerExecutor:

    def __init__(
        self,
        registry,
        contracts,
    ):

        self.node_executor = (
            NodeExecutor(

                registry,

                contracts,

            )
        )

    def execute_layer(

        self,

        layer,

        state,

        graph,

    ):

        results = {}

        for node_name in (
            layer.nodes
        ):

            node = (
                graph.nodes[
                    node_name
                ]
            )

            result = (
                self.node_executor
                .execute(

                    node,

                    state,

                    graph,

                )
            )

            results.update(
                result
            )

        return results