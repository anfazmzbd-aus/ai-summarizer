from app.orchestration.scheduler.scheduler import Scheduler
from app.orchestration.execution.execution_engine import ExecutionEngine
from app.orchestration.state.state_builder import StateBuilder
from app.orchestration.registry.agent_registry import AgentRegistry
from app.orchestration.registry.contract_manager import ContractManager
from app.orchestration.contracts.response_builder import ResponseBuilder
from app.runtime.runtime_manager import RuntimeManager
from app.services.llm_service import LLMService


class SummarizeService:

    def __init__(
        self,
        llm_service: LLMService | None = None,
    ) -> None:
        self._llm_service = llm_service

    def run(
        self,
        text,
    ):

        registry = AgentRegistry()

        contracts = ContractManager()

        scheduler = Scheduler(
            registry,
            contracts,
        )

        engine = ExecutionEngine(
            registry,
            contracts,
        )

        runtime = RuntimeManager(
            scheduler=scheduler,
            execution_engine=engine,
        )

        services = {}

        if self._llm_service is not None:
            services["llm_service"] = self._llm_service

        state = StateBuilder.build(
            text,
            services=services,
        )

        execution = runtime.run(
            text=text,
            contracts=contracts,
            state=state,
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
