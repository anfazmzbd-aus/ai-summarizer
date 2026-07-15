from app.orchestration.registry.agent_registry import AgentRegistry


class NodeExecutor:

    def __init__(
        self,
        registry: AgentRegistry,
        contracts,
    ):

        self.registry = registry
        self.contracts = contracts

    def execute(
        self,
        node,
        state,
    ):

        spec = self.registry.get(node)

        result = spec.agent.run(state)

        state.node_outputs[node] = result

        state.artifacts.update(result)

        self.contracts.validate_output(
            node,
            result,
        )

        return result
