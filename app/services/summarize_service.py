"""
AI Summarizer V9.1

Application-level summarization service.

Owns application runtime composition while preserving:
- deterministic Mock execution by default
- explicit LLM service injection
- provider-settings based runtime composition
- OpenRouter through the OpenAI-compatible provider
- the existing V8/V9 execution pipeline
"""

from __future__ import annotations

from app.orchestration.contracts.execution_response import ExecutionResponse
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
from app.providers.settings import ProviderSettings
from app.runtime.runtime_manager import RuntimeManager
from app.services.llm_service import LLMService


class SummarizeService:
    """
    Application service for document summarization.

    Default runtime:

        PromptRepository
            ↓
        PromptRegistry
            ↓
        PromptManager
            ↓
        AgentRegistry
            ↓
        ExecutionEngine
            ↓
        RuntimeManager
            ↓
        LLMService
            ↓
        MockProvider

    The default runtime remains deterministic and offline.

    Runtime configuration can be supplied through
    ``ProviderSettings``.

    Explicitly supplied ``LLMService`` always takes precedence
    over provider settings. This preserves dependency injection
    and existing integration behavior.
    """

    def __init__(
        self,
        llm_service: LLMService | None = None,
        prompt_manager: PromptManager | None = None,
        prompt_id: PromptId | None = None,
        prompt_version: PromptVersion | None = None,
        model: str | None = None,
        provider_settings: ProviderSettings | None = None,
    ) -> None:
        """
        Construct the summarization service.

        Runtime resolution order:

        1. Explicit ``llm_service``.
        2. Explicit ``provider_settings``.
        3. Deterministic MockProvider.

        No environment lookup occurs implicitly during the default
        constructor. This guarantees that normal tests and local
        development remain deterministic and offline.
        """

        if llm_service is None:
            factory = ProviderFactory()

            if provider_settings is not None:
                provider_runtime = ProviderRuntime.from_settings(
                    provider_settings,
                    factory=factory,
                )

                if model is None:
                    model = provider_settings.model

            else:
                factory.register(
                    ProviderType.MOCK,
                    MockProvider,
                )

                provider_runtime = ProviderRuntime.mock(
                    factory,
                    model=model or "mock-model",
                )

                if model is None:
                    model = "mock-model"

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
        self._provider_settings = provider_settings

    @classmethod
    def from_environment(
        cls,
        *,
        prompt_manager: PromptManager | None = None,
        prompt_id: PromptId | None = None,
        prompt_version: PromptVersion | None = None,
    ) -> "SummarizeService":
        """
        Construct a summarization service from environment settings.

        ProviderSettings owns environment parsing and validation.
        """

        settings = ProviderSettings.from_environment()

        return cls(
            provider_settings=settings,
            prompt_manager=prompt_manager,
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            model=settings.model,
        )

    @classmethod
    def from_openrouter(
        cls,
        *,
        api_key: str,
        model: str,
        endpoint: str = "https://openrouter.ai/api/v1",
        timeout: float = 60.0,
        max_retries: int = 2,
        prompt_manager: PromptManager | None = None,
        prompt_id: PromptId | None = None,
        prompt_version: PromptVersion | None = None,
    ) -> "SummarizeService":
        """
        Construct a summarization service using OpenRouter.

        OpenRouter is accessed through the existing OpenAI-compatible
        provider runtime. No separate provider abstraction is introduced.
        """

        factory = ProviderFactory()

        runtime = ProviderRuntime.openai(
            factory,
            api_key=api_key,
            model=model,
            endpoint=endpoint,
            timeout=timeout,
            max_retries=max_retries,
        )

        return cls(
            llm_service=runtime.service,
            prompt_manager=prompt_manager,
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            model=model,
        )

    def run(
        self,
        text: str,
    ) -> ExecutionResponse:
        """
        Execute a complete V9 summarization runtime cycle.

        Returns the complete ExecutionResponse contract.
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
