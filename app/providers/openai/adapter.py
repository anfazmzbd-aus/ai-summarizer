"""
AI Summarizer V9.1

OpenAI provider adapter.

Translates provider-specific responses and exceptions
into the generic LLM provider contract.
"""

from __future__ import annotations

import time

from app.providers.models import (
    FinishReason,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    MessageRole,
    Usage,
)

from .exceptions import (
    OpenAIAuthenticationError,
    OpenAIExecutionError,
    OpenAIRateLimitError,
    OpenAITimeoutError,
)


class OpenAIAdapter:
    """
    Adapter between OpenAI Responses API and the generic LLM contract.
    """

    def __init__(self, transport) -> None:
        self._transport = transport

    def execute(self, request: LLMRequest) -> LLMResponse:
        """
        Execute an LLM request through the OpenAI transport.

        Provider-specific exceptions are translated into
        V9.1 OpenAI provider exceptions.
        """

        start = time.perf_counter()

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

        except Exception as exc:
            raise self._translate_exception(exc) from exc

        latency_ms = (time.perf_counter() - start) * 1000

        usage = self._build_usage(response)

        response_model = getattr(
            response,
            "model",
            None,
        )

        model = response_model or request.model

        metadata = {
            "provider": "openai",
        }

        response_id = getattr(
            response,
            "id",
            None,
        )

        if response_id:
            metadata["response_id"] = response_id

        return LLMResponse(
            message=LLMMessage(
                role=MessageRole.ASSISTANT,
                content=getattr(
                    response,
                    "output_text",
                    "",
                ),
            ),
            model=model,
            finish_reason=FinishReason.STOP,
            usage=usage,
            latency_ms=latency_ms,
            metadata=metadata,
        )

    @staticmethod
    def _build_usage(response) -> Usage:
        """
        Normalize provider usage information.
        """

        provider_usage = getattr(
            response,
            "usage",
            None,
        )

        if provider_usage is None:
            return Usage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            )

        prompt_tokens = (
            getattr(
                provider_usage,
                "input_tokens",
                0,
            )
            or 0
        )

        completion_tokens = (
            getattr(
                provider_usage,
                "output_tokens",
                0,
            )
            or 0
        )

        total_tokens = getattr(
            provider_usage,
            "total_tokens",
            None,
        )

        if total_tokens is None:
            total_tokens = prompt_tokens + completion_tokens

        return Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    @staticmethod
    def _translate_exception(
        exc: Exception,
    ) -> Exception:
        """
        Translate provider/client exceptions into
        V9.1 domain-specific OpenAI exceptions.

        Classification is intentionally based on HTTP
        status information first, with class-name/message
        fallbacks for SDK and test doubles.
        """

        status_code = getattr(
            exc,
            "status_code",
            None,
        )

        response = getattr(
            exc,
            "response",
            None,
        )

        if status_code is None and response is not None:
            status_code = getattr(
                response,
                "status_code",
                None,
            )

        if status_code == 401:
            return OpenAIAuthenticationError(str(exc))

        if status_code == 403:
            return OpenAIAuthenticationError(str(exc))

        if status_code == 429:
            return OpenAIRateLimitError(str(exc))

        if isinstance(
            exc,
            TimeoutError,
        ):
            return OpenAITimeoutError(str(exc))

        exception_name = type(exc).__name__.lower()

        exception_message = str(exc).lower()

        if (
            "authentication" in exception_name
            or "authentication" in exception_message
            or "unauthorized" in exception_message
            or "invalid api key" in exception_message
        ):
            return OpenAIAuthenticationError(str(exc))

        if "permission" in exception_name or "forbidden" in exception_message:
            return OpenAIAuthenticationError(str(exc))

        if (
            "ratelimit" in exception_name
            or "rate_limit" in exception_name
            or "rate limit" in exception_message
            or "too many requests" in exception_message
        ):
            return OpenAIRateLimitError(str(exc))

        if (
            "timeout" in exception_name
            or "timed out" in exception_message
            or "timeout" in exception_message
        ):
            return OpenAITimeoutError(str(exc))

        return OpenAIExecutionError(str(exc))
