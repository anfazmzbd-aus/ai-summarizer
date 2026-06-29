from app.orchestration.scheduler.scheduler import (
    Scheduler,
)

from app.orchestration.execution.execution_engine import (
    ExecutionEngine,
)

from app.orchestration.state.state_builder import (
    StateBuilder,
)

from app.orchestration.registry.agent_registry import (
    AgentRegistry,
)

from app.orchestration.registry.contract_manager import (
    ContractManager,
)


class SummarizeService:

    def run(
        self,
        text,
    ):

        registry = (
            AgentRegistry()
        )

        contracts = (
            ContractManager()
        )

        scheduler = (
            Scheduler(
                registry
            )
        )

        engine = (
            ExecutionEngine(

                registry,

                contracts,

            )

        )

        plan = (
            scheduler
            .schedule(
                text
            )
        )

        state = (
            StateBuilder
            .build(
                text
            )
        )

        return (

            engine
            .execute(

                plan.graph,

                state,

            )

        )