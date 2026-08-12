from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.providers.models import (
    LLMMessage,
    LLMRequest,
    MessageRole,
)

from app.providers.openai.adapter import OpenAIAdapter
from app.providers.openai.exceptions import (
    OpenAIAuthenticationError,
    OpenAIExecutionError,
    OpenAIRateLimitError,
    OpenAITimeoutError,
)


def _request() -> LLMRequest:
    return LLMRequest(
        model="gpt-5",
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="hello",
            ),
        ),
    )


def _adapter_with_exception(exc: Exception) -> OpenAIAdapter:
    transport = Mock()

    transport.client.responses.create.side_effect = exc

    return OpenAIAdapter(transport)


def test_authentication_error_401():
    error = RuntimeError("Unauthorized")
    error.status_code = 401

    adapter = _adapter_with_exception(error)

    with pytest.raises(
        OpenAIAuthenticationError,
        match="Unauthorized",
    ):
        adapter.execute(_request())


def test_authentication_error_403():
    error = RuntimeError("Forbidden")
    error.status_code = 403

    adapter = _adapter_with_exception(error)

    with pytest.raises(
        OpenAIAuthenticationError,
        match="Forbidden",
    ):
        adapter.execute(_request())


def test_rate_limit_error():
    error = RuntimeError("Too many requests")
    error.status_code = 429

    adapter = _adapter_with_exception(error)

    with pytest.raises(
        OpenAIRateLimitError,
        match="Too many requests",
    ):
        adapter.execute(_request())


def test_timeout_error():
    adapter = _adapter_with_exception(TimeoutError("Request timed out"))

    with pytest.raises(
        OpenAITimeoutError,
        match="Request timed out",
    ):
        adapter.execute(_request())


def test_unknown_error_becomes_execution_error():
    adapter = _adapter_with_exception(RuntimeError("Unexpected failure"))

    with pytest.raises(
        OpenAIExecutionError,
        match="Unexpected failure",
    ):
        adapter.execute(_request())


def test_original_exception_is_preserved_as_cause():
    original = RuntimeError("provider failure")

    adapter = _adapter_with_exception(original)

    with pytest.raises(OpenAIExecutionError) as exc_info:
        adapter.execute(_request())

    assert exc_info.value.__cause__ is original


def test_successful_response_preserves_text_and_model():
    transport = Mock()

    transport.client.responses.create.return_value = SimpleNamespace(
        output_text="Generated summary",
        model="gpt-5",
        usage=SimpleNamespace(
            input_tokens=10,
            output_tokens=7,
            total_tokens=17,
        ),
    )

    adapter = OpenAIAdapter(transport)

    result = adapter.execute(_request())

    assert result.message.content == "Generated summary"
    assert result.model == "gpt-5"

    assert result.usage.prompt_tokens == 10
    assert result.usage.completion_tokens == 7
    assert result.usage.total_tokens == 17


def test_successful_response_without_usage_defaults_to_zero():
    transport = Mock()

    transport.client.responses.create.return_value = SimpleNamespace(
        output_text="Generated summary",
        model="gpt-5",
    )

    adapter = OpenAIAdapter(transport)

    result = adapter.execute(_request())

    assert result.message.content == "Generated summary"

    assert result.usage.prompt_tokens == 0
    assert result.usage.completion_tokens == 0
    assert result.usage.total_tokens == 0
