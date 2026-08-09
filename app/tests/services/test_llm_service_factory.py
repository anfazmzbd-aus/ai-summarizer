from unittest.mock import Mock

from app.providers.config import ProviderConfig, ProviderType
from app.providers.factory import ProviderFactory
from app.services.llm_service import LLMService
from app.services.llm_service_factory import LLMServiceFactory


def test_factory_creates_llm_service():
    provider_factory = Mock(spec=ProviderFactory)

    provider = Mock()
    provider.name = "mock"

    provider_factory.create.return_value = provider

    factory = LLMServiceFactory(provider_factory)

    config = ProviderConfig(
        provider=ProviderType.MOCK,
        model="test-model",
    )

    result = factory.create(config)

    assert isinstance(result, LLMService)
    assert result.provider_name == "mock"

    provider_factory.create.assert_called_once_with(config)
