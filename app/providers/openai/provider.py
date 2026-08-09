"""
AI Summarizer V9.1

OpenAI provider implementation.
"""

from __future__ import annotations

from app.providers.base import BaseProvider
from app.providers.capabilities import ProviderCapabilities
from app.providers.health import (
    ProviderHealth,
    ProviderStatus,
)

from .adapter import OpenAIAdapter


class OpenAIProvider(BaseProvider):
    """
    OpenAI provider implementation.
    """

    name = "openai"

    def __init__(self, adapter: OpenAIAdapter) -> None:
        self._adapter = adapter

    def chat(
        self,
        request,
    ):
        return self._adapter.execute(request)

    #
    # Existing BaseProvider contract
    #

    def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name,
            status=ProviderStatus.HEALTHY,
        )

    def supports_streaming(self) -> bool:
        return True

    def available_models(self) -> tuple[str, ...]:
        return (
            "gpt-5",
            "gpt-5-mini",
        )

    #
    # New V9 convenience API
    #

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            streaming=True,
            vision=True,
            tool_calling=True,
            structured_output=True,
            reasoning=True,
        )
