"""
AI Summarizer V9.x

Application-level summarization service.

Owns the default V9 runtime composition while preserving
the existing V8 execution pipeline.

The default construction remains deterministic and offline.
Live OpenAI-compatible providers are explicitly composed
through the existing ProviderRuntime boundary.
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
    integration scenarios, and production provider configuration.
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

    @classmethod
    def from_openai(
        cls,
        *,
        api_key: str,
        model: str = "gpt-5",
        organization: str | None = None,
        endpoint: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> "SummarizeService":
        """
        Construct a summarization service backed by the
        existing OpenAI-compatible provider runtime.

        This method does not introduce a new service abstraction.
        It composes the existing ProviderRuntime → LLMService path.

        `endpoint` supports OpenAI-compatible providers such as
        OpenRouter.
        """

        factory = ProviderFactory()

        provider_runtime = ProviderRuntime.openai(
            factory,
            api_key=api_key,
            model=model,
            organization=organization,
            endpoint=endpoint,
            timeout=timeout,
            max_retries=max_retries,
        )

        return cls(
            llm_service=provider_runtime.service,
            model=model,
        )

    @classmethod
    def from_openrouter(
        cls,
        *,
        api_key: str,
        model: str = "openai/gpt-5-mini",
        endpoint: str = "https://openrouter.ai/api/v1",
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> "SummarizeService":
        """
        Construct a summarization service backed by OpenRouter.

        OpenRouter exposes an OpenAI-compatible API, therefore the
        existing OpenAI provider implementation is reused.
        """

        return cls.from_openai(
            api_key=api_key,
            model=model,
            endpoint=endpoint,
            timeout=timeout,
            max_retries=max_retries,
        )

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
