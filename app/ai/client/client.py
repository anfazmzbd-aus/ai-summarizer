"""
Production LLM client.
"""

from __future__ import annotations

import asyncio

from app.ai import (
    AIProviderRegistry,
    AIRequest,
    AIResponse,
)

from .exceptions import (
    LLMClientError,
    LLMTimeoutError,
)
from .options import LLMOptions


class LLMClient:

    def __init__(
        self,
        registry: AIProviderRegistry,
        options: LLMOptions | None = None,
    ) -> None:

        self._registry = registry
        self._options = options or LLMOptions()

    async def generate(
        self,
        provider: str,
        request: AIRequest,
    ) -> AIResponse:

        service = self._registry.get(
            provider,
        )

        try:

            return await asyncio.wait_for(
                service.generate(request),
                timeout=self._options.timeout_seconds,
            )

        except TimeoutError as exc:

            raise LLMTimeoutError("LLM request timed out.") from exc

        except Exception as exc:

            raise LLMClientError(str(exc)) from exc
