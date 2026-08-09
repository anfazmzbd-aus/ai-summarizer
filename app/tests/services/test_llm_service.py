from unittest.mock import Mock

import pytest

from app.providers.config import ProviderConfig, ProviderType
from app.providers.factory import ProviderFactory
from app.providers.models import (
    FinishReason,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    MessageRole,
    Usage,
)
from app.services.llm_service import LLMService


def build_response() -> LLMResponse:
    return LLMResponse(
        message=LLMMessage(
            role=MessageRole.ASSISTANT,
            content="summary",
        ),
        model="mock-model",
        finish_reason=FinishReason.STOP,
        usage=Usage(),
        latency_ms=1.0,
    )


def test_llm_service_creates_provider_from_factory():
    provider = Mock()
    provider.name = "mock"

    factory = Mock(spec=ProviderFactory)
    factory.create.return_value = provider

    config = ProviderConfig(
        provider=ProviderType.MOCK,
        model="mock-model",
    )

    service = LLMService(
        factory=factory,
        config=config,
    )

    factory.create.assert_called_once_with(config)
    assert service.provider_name == "mock"


def test_llm_service_executes_request_through_provider():
    provider = Mock()
    provider.name = "mock"
    provider.chat.return_value = build_response()

    factory = Mock(spec=ProviderFactory)
    factory.create.return_value = provider

    config = ProviderConfig(
        provider=ProviderType.MOCK,
        model="mock-model",
    )

    service = LLMService(
        factory=factory,
        config=config,
    )

    request = LLMRequest(
        model="mock-model",
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="hello",
            ),
        ),
    )

    result = service.execute(request)

    provider.chat.assert_called_once_with(request)
    assert result.message.content == "summary"
    assert result.model == "mock-model"


def test_llm_service_preserves_provider_response():
    provider = Mock()
    provider.name = "mock"

    expected = build_response()

    provider.chat.return_value = expected

    factory = Mock(spec=ProviderFactory)
    factory.create.return_value = provider

    config = ProviderConfig(
        provider=ProviderType.MOCK,
        model="mock-model",
    )

    service = LLMService(
        factory=factory,
        config=config,
    )

    request = LLMRequest(
        model="mock-model",
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="hello",
            ),
        ),
    )

    result = service.execute(request)

    assert result is expected


def test_llm_service_propagates_provider_error():
    provider = Mock()
    provider.name = "mock"
    provider.chat.side_effect = RuntimeError("provider failure")

    factory = Mock(spec=ProviderFactory)
    factory.create.return_value = provider

    config = ProviderConfig(
        provider=ProviderType.MOCK,
        model="mock-model",
    )

    service = LLMService(
        factory=factory,
        config=config,
    )

    request = LLMRequest(
        model="mock-model",
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="hello",
            ),
        ),
    )

    with pytest.raises(RuntimeError, match="provider failure"):
        service.execute(request)
