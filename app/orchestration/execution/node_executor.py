from app.orchestration.state.state_model import State


class NodeExecutor:

    def __init__(
        self,
        registry,
        contracts,
    ):
        self.registry = registry
        self.contracts = contracts

    def execute(
        self,
        node,
        state: State,
        graph,
    ):

        execution_input = {

            "global_context":
                state.global_context,

            "artifacts":
                state.artifacts,

            "node_outputs":
                state.node_outputs,
        }

        self.contracts.validate_input(
            node.function_name,
            execution_input,
        )

        agent = (
            self.registry
            .resolve(
                node.function_name
            )
        )

        output = (
            agent.run(
                execution_input
            )
        )

        self.contracts.validate_output(
            node.function_name,
            output,
        )

        return {

            node.name:
            output

        }