"""
AI Summarizer V9.1

Application-level construction of the LLM service.
"""

from __future__ import annotations

from app.providers.config import ProviderConfig
from app.providers.factory import ProviderFactory
from app.services.llm_service import LLMService


class LLMServiceFactory:
    """
    Constructs LLMService instances from provider configuration.
    """

    def __init__(self, provider_factory: ProviderFactory) -> None:
        self._provider_factory = provider_factory

    def create(
        self,
        config: ProviderConfig,
    ) -> LLMService:
        """
        Create an LLMService using the configured provider.
        """

        return LLMService(
            factory=self._provider_factory,
            config=config,
        )
