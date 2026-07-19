from app.orchestration.execution.node_executor import NodeExecutor


class LayerExecutor:

    def __init__(self, registry, contracts):

        self.node_executor = NodeExecutor(registry, contracts)

    def execute_layer(self, layer, state):

        results = []

        for node in layer.nodes:
            execution = self.node_executor.execute(
                node,
                state,
            )

            state.node_outputs[execution.node] = execution.output

            state.artifacts.update(execution.output)
            results.append(execution)

        return results
