"""
AI Summarizer V9.x

Application-level summarization service.

The service owns runtime composition for a summarization request while
preserving the existing V8 execution pipeline.
"""

from __future__ import annotations

from app.orchestration.contracts.response_builder import ResponseBuilder
from app.orchestration.execution.execution_engine import ExecutionEngine
from app.orchestration.registry.agent_registry import AgentRegistry
from app.orchestration.registry.contract_manager import ContractManager
from app.orchestration.scheduler.scheduler import Scheduler
from app.orchestration.state.state_builder import StateBuilder
from app.prompts.manager import PromptManager
from app.prompts.value_objects import PromptId, PromptVersion
from app.runtime.runtime_manager import RuntimeManager
from app.services.llm_service import LLMService


class SummarizeService:
    """
    Application service for document summarization.

    V8 compatibility:
        If no V9 dependencies are supplied, AgentRegistry retains its
        legacy-compatible behavior.

    V9 runtime:
        PromptManager and LLMService are injected into AgentRegistry so
        SummaryAgent can execute through the provider runtime.
    """

    def __init__(
        self,
        llm_service: LLMService | None = None,
        prompt_manager: PromptManager | None = None,
        prompt_id: PromptId | None = None,
        prompt_version: PromptVersion | None = None,
        model: str | None = None,
    ) -> None:
        self._llm_service = llm_service
        self._prompt_manager = prompt_manager
        self._prompt_id = prompt_id
        self._prompt_version = prompt_version
        self._model = model

    def run(
        self,
        text: str,
    ):
        """
        Execute a complete summarization runtime cycle.
        """

        registry = AgentRegistry(
            prompt_manager=self._prompt_manager,
            llm_service=self._llm_service,
            prompt_id=self._prompt_id,
            prompt_version=self._prompt_version,
            model=self._model,
        )

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
