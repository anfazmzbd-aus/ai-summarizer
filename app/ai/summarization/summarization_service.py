"""
Production summarization service.
"""

from __future__ import annotations

from app.ai.runtime import (
    AIRuntimeRequest,
    AIRuntimeService,
)

from .summarization_config import SummarizationConfig
from .summarization_request import SummarizationRequest
from .summarization_response import SummarizationResponse


class SummarizationService:

    def __init__(
        self,
        runtime: AIRuntimeService,
        config: SummarizationConfig | None = None,
    ) -> None:

        self._runtime = runtime
        self._config = config or SummarizationConfig()

    async def summarize(
        self,
        request: SummarizationRequest,
    ) -> SummarizationResponse:

        runtime_response = await self._runtime.generate(
            AIRuntimeRequest(
                provider=request.provider,
                prompt_name=request.prompt_name,
                model=request.model,
                variables={
                    "text": request.text,
                },
            )
        )

        response = runtime_response.response

        return SummarizationResponse(
            summary=response.text,
            prompt=runtime_response.prompt,
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
        )
