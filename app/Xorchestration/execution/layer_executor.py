from app.orchestration.execution.node_executor import NodeExecutor
from app.orchestration.registry.agent_registry import AgentRegistry
from app.orchestration.registry.contract_manager import ContractManager
from app.orchestration.graph.graph_schema import ExecutionLayer
from app.orchestration.state.state_model import State


class LayerExecutor:

    def __init__(
        self,
        registry: AgentRegistry,
        contracts: ContractManager,
    ):

        self.node_executor = NodeExecutor(
            registry=registry,
            contracts=contracts,
        )

    # -------------------------
    # Execute Layer
    # -------------------------

    def execute_layer(
        self,
        layer: ExecutionLayer,
        state: State,
        graph,
    ):

        results = {}

        for node_name in layer.nodes:

            node = graph.nodes[node_name]

            result = self.node_executor.execute(
                node=node,
                state=state,
            )

            results[node_name] = result

        return results