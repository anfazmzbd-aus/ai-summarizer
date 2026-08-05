"""
Production AI runtime service.
"""

from __future__ import annotations

from app.ai import (
    AIRequest,
    LLMClient,
    PromptEngine,
)

from .runtime_config import AIRuntimeConfig
from .runtime_request import AIRuntimeRequest
from .runtime_response import AIRuntimeResponse


class AIRuntimeService:

    def __init__(
        self,
        prompt_engine: PromptEngine,
        client: LLMClient,
        config: AIRuntimeConfig | None = None,
    ) -> None:

        self._prompt_engine = prompt_engine
        self._client = client
        self._config = config or AIRuntimeConfig()

    async def generate(
        self,
        request: AIRuntimeRequest,
    ) -> AIRuntimeResponse:

        prompt = self._prompt_engine.render(
            request.prompt_name,
            **request.variables,
        )

        response = await self._client.generate(
            request.provider,
            AIRequest(
                prompt=prompt,
                model=request.model,
                temperature=self._config.default_temperature,
                max_tokens=self._config.default_max_tokens,
            ),
        )

        return AIRuntimeResponse(
            prompt=prompt,
            response=response,
        )
