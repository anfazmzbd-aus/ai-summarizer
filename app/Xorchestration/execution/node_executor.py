from dataclasses import dataclass
from typing import Any
from typing import Dict

from app.orchestration.graph.graph_schema import (
    GraphNode,
)

from app.orchestration.registry.agent_registry import (
    AgentRegistry,
)

from app.orchestration.registry.contract_manager import (
    ContractManager,
)

from app.orchestration.state.state_model import (
    State,
)


# -------------------------
# Execution Result
# -------------------------

@dataclass(frozen=True)
class NodeExecutionResult:

    node_name: str

    output: Dict[
        str,
        Any
    ]

    duration_ms: float = 0


# -------------------------
# Node Executor
# -------------------------

class NodeExecutor:

    def __init__(

        self,

        registry: AgentRegistry,

        contracts: ContractManager,

    ):

        self.registry = (
            registry
        )

        self.contracts = (
            contracts
        )

    # -------------------------
    # Build Input
    # -------------------------

    def _build_input(

        self,

        node: GraphNode,

        state: State,

    ):

        return {

            "global_context":
            state.global_context,

            "artifacts":
            state.artifacts,

            "node_outputs":
            state.node_outputs,

        }

    # -------------------------
    # Execute
    # -------------------------

    def execute(

        self,

        node: GraphNode,

        state: State,

    ) -> NodeExecutionResult:

        execution_input = (

            self._build_input(

                node,

                state,

            )

        )

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

        return (

            NodeExecutionResult(

                node_name=node.name,

                output=output,

            )

        )