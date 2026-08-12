from unittest.mock import Mock

from app.providers.config import ProviderType
from app.providers.factory import ProviderFactory
from app.providers.runtime import ProviderRuntime
from app.providers.settings import ProviderSettings


def test_runtime_from_mock_settings():
    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="mock-model",
    )

    runtime = ProviderRuntime.from_settings(
        settings,
    )

    assert runtime.provider_type is ProviderType.MOCK
    assert runtime.provider_name == "mock"
    assert runtime.service is not None


def test_runtime_from_mock_settings_reuses_factory():
    factory = ProviderFactory()

    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="test-model",
    )

    runtime = ProviderRuntime.from_settings(
        settings,
        factory=factory,
    )

    assert runtime.provider_type is ProviderType.MOCK
    assert factory.supported_providers() == (ProviderType.MOCK,)


def test_runtime_from_openai_settings_registers_provider():
    factory = ProviderFactory()

    settings = ProviderSettings(
        provider=ProviderType.OPENAI,
        model="gpt-5-mini",
        api_key="test-key",
        endpoint="https://example.test",
    )

    creator = Mock()

    factory.register(
        ProviderType.OPENAI,
        creator,
    )

    runtime = ProviderRuntime.from_settings(
        settings,
        factory=factory,
    )

    assert runtime.provider_type is ProviderType.OPENAI
    assert runtime._config.model == "gpt-5-mini"
    assert runtime._config.api_key == "test-key"
    assert runtime._config.endpoint == "https://example.test"


def test_runtime_from_openai_settings_passes_configuration():
    factory = ProviderFactory()

    creator = Mock()

    factory.register(
        ProviderType.OPENAI,
        creator,
    )

    settings = ProviderSettings(
        provider=ProviderType.OPENAI,
        model="openai/gpt-5-mini",
        api_key="test-key",
        endpoint="https://openrouter.ai/api/v1",
        organization="test-org",
        timeout=30.0,
        max_retries=1,
    )

    runtime = ProviderRuntime.from_settings(
        settings,
        factory=factory,
    )

    assert runtime.provider_type is ProviderType.OPENAI

    config = runtime._config

    assert config.provider is ProviderType.OPENAI
    assert config.model == "openai/gpt-5-mini"
    assert config.api_key == "test-key"
    assert config.endpoint == "https://openrouter.ai/api/v1"
    assert config.organization == "test-org"
    assert config.timeout == 30.0
    assert config.max_retries == 1
