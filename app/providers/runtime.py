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

        return cls(
            factory,
            ProviderConfig(
                provider=ProviderType.MOCK,
                model=model,
            ),
        )
