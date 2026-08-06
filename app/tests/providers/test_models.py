from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.providers.models import (
    FinishReason,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    MessageRole,
    Usage,
)


def test_message_creation():
    message = LLMMessage(
        role=MessageRole.USER,
        content="Hello",
    )

    assert message.role is MessageRole.USER
    assert message.content == "Hello"
    assert message.name is None


def test_usage_defaults():
    usage = Usage()

    assert usage.prompt_tokens == 0
    assert usage.completion_tokens == 0
    assert usage.total_tokens == 0


def test_request_creation():
    request = LLMRequest(
        messages=(
            LLMMessage(
                role=MessageRole.SYSTEM,
                content="You are helpful.",
            ),
            LLMMessage(
                role=MessageRole.USER,
                content="Summarize this.",
            ),
        ),
        model="gpt-5",
    )

    assert request.model == "gpt-5"
    assert len(request.messages) == 2
    assert request.stream is False
    assert request.temperature == 0.2


def test_response_creation():
    response = LLMResponse(
        message=LLMMessage(
            role=MessageRole.ASSISTANT,
            content="Summary",
        ),
        model="gpt-5",
        finish_reason=FinishReason.STOP,
        usage=Usage(
            prompt_tokens=10,
            completion_tokens=15,
            total_tokens=25,
        ),
        latency_ms=52.3,
    )

    assert response.model == "gpt-5"
    assert response.finish_reason is FinishReason.STOP
    assert response.usage.total_tokens == 25


def test_models_are_frozen():
    message = LLMMessage(
        role=MessageRole.USER,
        content="abc",
    )

    with pytest.raises(FrozenInstanceError):
        message.content = "changed"


def test_enum_values():
    assert MessageRole.SYSTEM.value == "system"
    assert MessageRole.USER.value == "user"
    assert MessageRole.ASSISTANT.value == "assistant"
    assert MessageRole.TOOL.value == "tool"

    assert FinishReason.STOP.value == "stop"
    assert FinishReason.LENGTH.value == "length"
