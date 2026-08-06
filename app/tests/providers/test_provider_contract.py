from __future__ import annotations

import pytest

from app.providers.base import BaseProvider
from app.providers.models import (
    FinishReason,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    MessageRole,
    Usage,
)
from app.providers.health import (
    ProviderHealth,
    ProviderStatus,
)


class DummyProvider(BaseProvider):

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def supports_streaming(self) -> bool:
        return False

    def health_check(self) -> ProviderHealth:
        return ProviderHealth.healthy(
            provider=self.name,
            latency_ms=1.5,
        )

    def available_models(self) -> tuple[str, ...]:
        return ("dummy-model",)

    def chat(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        return LLMResponse(
            message=LLMMessage(
                role=MessageRole.ASSISTANT,
                content="dummy response",
            ),
            model="dummy-model",
            finish_reason=FinishReason.STOP,
            usage=Usage(),
            latency_ms=0.0,
        )


def test_provider_name():
    provider = DummyProvider()

    assert provider.name == "dummy"


def test_provider_streaming():
    provider = DummyProvider()

    assert provider.supports_streaming is False


def test_provider_health():
    provider = DummyProvider()

    health = provider.health_check()

    assert health.status is ProviderStatus.HEALTHY
    assert health.provider == "dummy"


def test_provider_models():
    provider = DummyProvider()

    assert provider.available_models() == ("dummy-model",)


def test_provider_chat():
    provider = DummyProvider()

    request = LLMRequest(
        model="dummy-model",
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="Hello",
            ),
        ),
    )

    response = provider.chat(request)

    assert response.message.content == "dummy response"
    assert response.model == "dummy-model"


def test_base_provider_is_abstract():
    with pytest.raises(TypeError):
        BaseProvider()
