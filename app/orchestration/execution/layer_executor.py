from app.orchestration.execution.node_executor import NodeExecutor


class LayerExecutor:

    def __init__(self, registry, contracts):

        self.node_executor = NodeExecutor(registry, contracts)

    def execute_layer(self, layer, state):

        results = []

        for node in layer.nodes:
            result = self.node_executor.execute(node, state)
            results.append(result)

        return results
