"""
AI Summarizer V9.1

OpenAI request adapter.
"""

from __future__ import annotations

from app.providers.models import (
    LLMRequest,
    LLMResponse,
)

from .exceptions import (
    OpenAIExecutionError,
)

from .transport import OpenAITransport

from app.providers.models import (
    FinishReason,
    LLMMessage,
    MessageRole,
    Usage,
)


class OpenAIAdapter:
    """
    Converts internal requests into
    OpenAI API calls.
    """

    def __init__(
        self,
        transport: OpenAITransport,
    ) -> None:

        self._transport = transport

    def execute(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        try:

            response = self._transport.client.responses.create(
                model=request.model,
                input=[
                    {
                        "role": message.role.value,
                        "content": message.content,
                    }
                    for message in request.messages
                ],
            )

            return LLMResponse(
                message=LLMMessage(
                    role=MessageRole.ASSISTANT,
                    content=response.output_text,
                ),
                model=request.model,
                finish_reason=FinishReason.STOP,
                usage=Usage(),
                latency_ms=0.0,
                metadata={},
            )

        except Exception as exc:

            raise OpenAIExecutionError(str(exc)) from exc
