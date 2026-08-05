"""
OpenAI-compatible provider.
"""

from __future__ import annotations

from openai import AsyncOpenAI

from app.ai import (
    AIProvider,
    AIRequest,
    AIResponse,
)

from .openai_config import OpenAIConfig


class OpenAIProvider(AIProvider):

    def __init__(
        self,
        config: OpenAIConfig,
    ) -> None:

        self._config = config

        kwargs = {
            "api_key": config.api_key,
        }

        if config.base_url:
            kwargs["base_url"] = config.base_url

        if config.organization:
            kwargs["organization"] = config.organization

        self._client = AsyncOpenAI(**kwargs)

    @property
    def name(self) -> str:

        return "openai"

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:

        response = await self._client.responses.create(
            model=request.model,
            input=request.prompt,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
        )

        usage = getattr(
            response,
            "usage",
            None,
        )

        return AIResponse(
            text=response.output_text,
            model=request.model,
            prompt_tokens=(usage.input_tokens if usage else 0),
            completion_tokens=(usage.output_tokens if usage else 0),
            metadata={
                "response_id": response.id,
            },
        )
