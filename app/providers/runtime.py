"""
AI Summarizer V9.1

Provider runtime composition.

Provides the composition boundary between provider configuration,
factory creation, and LLM service execution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.providers.config import (
    ProviderConfig,
    ProviderType,
)
from app.providers.factory import ProviderFactory
from app.providers.mock_provider import MockProvider

if TYPE_CHECKING:
    from app.services.llm_service import LLMService


class ProviderRuntime:
    """
    Composes the configured provider and LLM service.

    The LLMService import is intentionally deferred until runtime
    construction to avoid coupling the provider package's import
    path to the legacy service/orchestration package initialization.
    """

    def __init__(
        self,
        factory: ProviderFactory,
        config: ProviderConfig,
    ) -> None:
        from app.services.llm_service import LLMService

        self._factory = factory
        self._config = config
        self._service = LLMService(
            factory,
            config,
        )

    @property
    def service(self) -> "LLMService":
        """Return the configured LLM service."""

        return self._service

    @property
    def provider_name(self) -> str:
        """Return the active provider name."""

        return self._service.provider_name

    @property
    def provider_type(self) -> ProviderType:
        """Return the configured provider type."""

        return self._config.provider

    @classmethod
    def mock(
        cls,
        factory: ProviderFactory,
        *,
        model: str = "mock-model",
    ) -> "ProviderRuntime":
        """
        Construct a runtime configured for MockProvider.
        """

        if ProviderType.MOCK not in factory.supported_providers():
            factory.register(
                ProviderType.MOCK,
                MockProvider,
            )

        return cls(
            factory,
            ProviderConfig(
                provider=ProviderType.MOCK,
                model=model,
            ),
        )

    @classmethod
    def openai(
        cls,
        factory: ProviderFactory,
        *,
        api_key: str,
        model: str = "gpt-5",
        organization: str | None = None,
        endpoint: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> "ProviderRuntime":
        """
        Construct a runtime configured for OpenAI.

        The OpenAI provider is registered lazily so importing the
        generic provider runtime does not force OpenAI SDK setup.
        """

        if not api_key.strip():
            raise ValueError("OpenAI API key cannot be empty.")

        if ProviderType.OPENAI not in factory.supported_providers():
            from app.providers.openai.provider import (
                create_openai_provider,
            )

            factory.register(
                ProviderType.OPENAI,
                create_openai_provider,
            )

        return cls(
            factory,
            ProviderConfig(
                provider=ProviderType.OPENAI,
                model=model,
                api_key=api_key,
                organization=organization,
                endpoint=endpoint,
                timeout=timeout,
                max_retries=max_retries,
            ),
        )

    @classmethod
    def from_settings(
        cls,
        settings,
        *,
        factory: ProviderFactory | None = None,
    ) -> "ProviderRuntime":
        """
        Construct a provider runtime from application settings.

        Existing explicit runtime constructors remain supported.
        """

        factory = factory or ProviderFactory()

        if settings.provider is ProviderType.MOCK:
            return cls.mock(
                factory,
                model=settings.model,
            )

        if settings.provider is ProviderType.OPENAI:
            return cls.openai(
                factory,
                api_key=settings.api_key or "",
                model=settings.model,
                organization=settings.organization,
                endpoint=settings.endpoint,
                timeout=settings.timeout,
                max_retries=settings.max_retries,
            )

        config = ProviderConfig(
            provider=settings.provider,
            model=settings.model,
            api_key=settings.api_key,
            endpoint=settings.endpoint,
            organization=settings.organization,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
        )

        return cls(
            factory,
            config,
        )
