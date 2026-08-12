"""
AI Summarizer V9.1

OpenAI provider implementation.
"""

from __future__ import annotations

from app.providers.base import BaseProvider
from app.providers.capabilities import ProviderCapabilities
from app.providers.config import ProviderConfig
from app.providers.health import (
    ProviderHealth,
    ProviderStatus,
)

from .adapter import OpenAIAdapter
from .config import OpenAIConfig
from .transport import OpenAITransport


class OpenAIProvider(BaseProvider):
    """
    OpenAI provider implementation.
    """

    name = "openai"

    def __init__(self, adapter: OpenAIAdapter) -> None:
        self._adapter = adapter

    def chat(self, request):
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
    # V9 convenience API
    #

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            streaming=True,
            vision=True,
            tool_calling=True,
            structured_output=True,
            reasoning=True,
        )


def create_openai_provider(config: ProviderConfig) -> BaseProvider:
    """
    Create an OpenAI provider from the generic provider configuration.

    The generic ProviderConfig remains the factory boundary while the
    OpenAI-specific configuration is created internally.
    """

    if not config.api_key:
        raise ValueError("OpenAI provider requires an API key.")

    openai_config = OpenAIConfig(
        api_key=config.api_key,
        model=config.model,
        organization=config.organization,
        base_url=config.endpoint,
        timeout=config.timeout,
        max_retries=config.max_retries,
    )

    transport = OpenAITransport(openai_config)
    adapter = OpenAIAdapter(transport)

    return OpenAIProvider(adapter)
