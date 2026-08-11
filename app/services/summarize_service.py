"""
AI Summarizer V9.x

Application-level summarization service.

Owns the default V9 runtime composition while preserving
the existing V8 execution pipeline.
"""

from __future__ import annotations

from app.orchestration.contracts.response_builder import ResponseBuilder
from app.orchestration.execution.execution_engine import ExecutionEngine
from app.orchestration.registry.agent_registry import AgentRegistry
from app.orchestration.registry.contract_manager import ContractManager
from app.orchestration.scheduler.scheduler import Scheduler
from app.orchestration.state.state_builder import StateBuilder
from app.prompts.bootstrap import register_prompt
from app.prompts.manager import PromptManager
from app.prompts.repository import InMemoryPromptRepository
from app.prompts.registry import PromptRegistry
from app.prompts.templates.summary import (
    SUMMARY_PROMPT_ID,
    SUMMARY_PROMPT_VERSION,
    build_summary_prompt,
)
from app.prompts.value_objects import PromptId, PromptVersion
from app.providers.config import ProviderType
from app.providers.factory import ProviderFactory
from app.providers.mock_provider import MockProvider
from app.providers.runtime import ProviderRuntime
from app.runtime.runtime_manager import RuntimeManager
from app.services.llm_service import LLMService


class SummarizeService:
    """
    Application service for document summarization.

    Default V9 runtime:

        PromptRepository
            ↓
        PromptRegistry
            ↓
        PromptManager
            ↓
        SummaryAgent
            ↓
        LLMService
            ↓
        MockProvider

    The default provider remains deterministic and offline.

    Explicitly injected LLM services are preserved for tests,
    integration scenarios, and future production configuration.
    """

    def __init__(
        self,
        llm_service: LLMService | None = None,
        prompt_manager: PromptManager | None = None,
        prompt_id: PromptId | None = None,
        prompt_version: PromptVersion | None = None,
        model: str | None = None,
    ) -> None:
        if llm_service is None:
            factory = ProviderFactory()

            factory.register(
                ProviderType.MOCK,
                MockProvider,
            )

            provider_runtime = ProviderRuntime.mock(
                factory,
                model=model or "mock-model",
            )

            llm_service = provider_runtime.service

        if prompt_manager is None:
            repository = InMemoryPromptRepository()

            register_prompt(
                repository,
                build_summary_prompt(),
            )

            prompt_manager = PromptManager(
                PromptRegistry(repository),
            )

        self._llm_service = llm_service
        self._prompt_manager = prompt_manager
        self._prompt_id = prompt_id or SUMMARY_PROMPT_ID
        self._prompt_version = prompt_version or SUMMARY_PROMPT_VERSION
        self._model = model or "mock-model"

    def run(
        self,
        text: str,
    ):
        """
        Execute a complete V9 summarization runtime cycle.
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

        services = {
            "llm_service": self._llm_service,
        }

        state = StateBuilder.build(
            text,
            services=services,
        )

        execution = runtime.run(
            text=text,
            contracts=contracts,
            state=state,
        )

        response = ResponseBuilder.build(
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

        return response
