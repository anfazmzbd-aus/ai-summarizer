"""
AI Summarizer V9.0

Deterministic mock LLM provider.

Used for offline development and testing.
"""

from __future__ import annotations

import time

from .base import BaseProvider
from .config import ProviderConfig
from .health import ProviderHealth
from .models import (
    FinishReason,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    MessageRole,
    Usage,
)


class MockProvider(BaseProvider):
    """
    Deterministic provider implementation.

    This provider never communicates externally.
    """

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        self._config = config

    @property
    def name(self) -> str:
        return "mock"

    @property
    def supports_streaming(self) -> bool:
        return False

    def chat(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Generate deterministic response.
        """

        start = time.perf_counter()

        response_message = LLMMessage(
            role=MessageRole.ASSISTANT,
            content=("Mock response generated " "successfully."),
        )

        latency = (time.perf_counter() - start) * 1000

        return LLMResponse(
            message=response_message,
            model=self._config.model,
            finish_reason=FinishReason.STOP,
            usage=Usage(
                prompt_tokens=len(request.messages),
                completion_tokens=5,
                total_tokens=(len(request.messages) + 5),
            ),
            latency_ms=latency,
        )

    def health_check(self) -> ProviderHealth:
        return ProviderHealth.healthy(
            provider=self.name,
            latency_ms=0.1,
        )

    def available_models(self) -> tuple[str, ...]:
        return (self._config.model,)
