"""
AI Summarizer V9.0

LLM service abstraction.

Provides a runtime-facing interface for
executing LLM requests.
"""

from __future__ import annotations

from app.providers.config import ProviderConfig
from app.providers.factory import ProviderFactory
from app.providers.models import (
    LLMRequest,
    LLMResponse,
)


class LLMService:
    """
    Runtime service for LLM execution.
    """

    def __init__(
        self,
        factory: ProviderFactory,
        config: ProviderConfig,
    ) -> None:

        self._provider = factory.create(config)

    @property
    def provider_name(self) -> str:
        return self._provider.name

    def execute(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Execute an LLM request.
        """

        return self._provider.chat(request)
