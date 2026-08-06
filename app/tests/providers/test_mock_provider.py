from app.providers.config import (
    ProviderConfig,
    ProviderType,
)
from app.providers.health import (
    ProviderStatus,
)
from app.providers.mock_provider import (
    MockProvider,
)
from app.providers.models import (
    LLMMessage,
    LLMRequest,
    MessageRole,
)


def create_provider() -> MockProvider:

    config = ProviderConfig(
        provider=ProviderType.MOCK,
        model="mock-model",
    )

    return MockProvider(config)


def test_provider_name():

    provider = create_provider()

    assert provider.name == "mock"


def test_provider_streaming():

    provider = create_provider()

    assert provider.supports_streaming is False


def test_available_models():

    provider = create_provider()

    assert provider.available_models() == ("mock-model",)


def test_chat_response():

    provider = create_provider()

    request = LLMRequest(
        model="mock-model",
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="Summarize this",
            ),
        ),
    )

    response = provider.chat(request)

    assert response.model == "mock-model"

    assert response.message.content == "Mock response generated successfully."


def test_health_check():

    provider = create_provider()

    health = provider.health_check()

    assert health.status is ProviderStatus.HEALTHY
    assert health.provider == "mock"
