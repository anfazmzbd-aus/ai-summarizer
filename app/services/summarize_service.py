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

from app.orchestration.contracts.response_builder import (
    ResponseBuilder,
)


class SummarizeService:

    def run(
        self,
        text,
    ):

        registry = AgentRegistry()

        contracts = ContractManager()

        scheduler = Scheduler(registry, contracts)

        engine = ExecutionEngine(
            registry,
            contracts,
        )

        plan = scheduler.schedule(text, contracts)

        state = StateBuilder.build(text)

        execution = engine.execute(
            plan.graph,
            state,
        )

        return ResponseBuilder.build(
            state=execution.state,
            trace=getattr(
                engine,
                "trace",
                None,
            ),
            metrics=getattr(
                engine,
                "metrics",
                None,
            ),
        )
