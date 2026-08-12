from unittest.mock import Mock

from app.providers.models import (
    FinishReason,
    LLMMessage,
    LLMRequest,
    MessageRole,
)

from app.providers.openai.adapter import (
    OpenAIAdapter,
)

from app.providers.openai.exceptions import (
    OpenAIExecutionError,
)


def build_request() -> LLMRequest:
    return LLMRequest(
        model="gpt-5",
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="hello",
            ),
        ),
    )


def test_execute():
    transport = Mock()

    response = Mock(
        output_text="summary",
        model="gpt-5",
        id="resp_test_123",
    )

    response.usage = Mock(
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
    )

    transport.client.responses.create.return_value = response

    adapter = OpenAIAdapter(transport)

    result = adapter.execute(build_request())

    assert result.message.content == "summary"
    assert result.message.role is MessageRole.ASSISTANT
    assert result.model == "gpt-5"
    assert result.finish_reason is FinishReason.STOP

    transport.client.responses.create.assert_called_once()


def test_execute_normalizes_usage():
    transport = Mock()

    response = Mock(
        output_text="summary",
        model="gpt-5",
        id="resp_usage_123",
    )

    response.usage = Mock(
        input_tokens=42,
        output_tokens=17,
        total_tokens=59,
    )

    transport.client.responses.create.return_value = response

    adapter = OpenAIAdapter(transport)

    result = adapter.execute(build_request())

    assert result.usage.prompt_tokens == 42
    assert result.usage.completion_tokens == 17
    assert result.usage.total_tokens == 59


def test_execute_captures_response_metadata():
    transport = Mock()

    response = Mock(
        output_text="summary",
        model="gpt-5-mini",
        id="resp_metadata_123",
    )

    response.usage = Mock(
        input_tokens=8,
        output_tokens=4,
        total_tokens=12,
    )

    transport.client.responses.create.return_value = response

    adapter = OpenAIAdapter(transport)

    result = adapter.execute(build_request())

    assert result.metadata["provider"] == "openai"
    assert result.metadata["response_id"] == ("resp_metadata_123")


def test_execute_captures_latency():
    transport = Mock()

    response = Mock(
        output_text="summary",
        model="gpt-5",
        id="resp_latency_123",
    )

    response.usage = Mock(
        input_tokens=1,
        output_tokens=1,
        total_tokens=2,
    )

    transport.client.responses.create.return_value = response

    adapter = OpenAIAdapter(transport)

    result = adapter.execute(build_request())

    assert result.latency_ms >= 0.0


def test_execute_handles_missing_usage():
    transport = Mock()

    response = Mock(
        output_text="summary",
        model="gpt-5",
        id="resp_no_usage",
    )

    response.usage = None

    transport.client.responses.create.return_value = response

    adapter = OpenAIAdapter(transport)

    result = adapter.execute(build_request())

    assert result.usage.prompt_tokens == 0
    assert result.usage.completion_tokens == 0
    assert result.usage.total_tokens == 0


def test_execute_uses_request_model_when_response_model_missing():
    transport = Mock()

    response = Mock(
        output_text="summary",
        id="resp_model_fallback",
    )

    response.model = None

    response.usage = Mock(
        input_tokens=3,
        output_tokens=2,
        total_tokens=5,
    )

    transport.client.responses.create.return_value = response

    adapter = OpenAIAdapter(transport)

    result = adapter.execute(build_request())

    assert result.model == "gpt-5"


def test_execute_wraps_provider_exception():
    transport = Mock()

    transport.client.responses.create.side_effect = RuntimeError("provider unavailable")

    adapter = OpenAIAdapter(transport)

    try:
        adapter.execute(build_request())
    except OpenAIExecutionError as exc:
        assert str(exc) == "provider unavailable"
    else:
        raise AssertionError("Expected OpenAIExecutionError")
