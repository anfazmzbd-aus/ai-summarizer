from app.providers.config import (
    ProviderConfig,
    ProviderType,
)
from app.providers.factory import (
    ProviderFactory,
)
from app.providers.mock_provider import (
    MockProvider,
)
from app.providers.models import (
    LLMMessage,
    LLMRequest,
    MessageRole,
)
from app.services.llm_service import (
    LLMService,
)


def create_service():

    factory = ProviderFactory()

    factory.register(
        ProviderType.MOCK,
        MockProvider,
    )

    config = ProviderConfig(
        provider=ProviderType.MOCK,
        model="mock-model",
    )

    return LLMService(
        factory,
        config,
    )


def test_service_provider():

    service = create_service()

    assert service.provider_name == "mock"


def test_service_execution():

    service = create_service()

    request = LLMRequest(
        model="mock-model",
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="Summarize",
            ),
        ),
    )

    response = service.execute(request)

    assert response.model == "mock-model"

    assert response.message.content == "Mock response generated successfully."
