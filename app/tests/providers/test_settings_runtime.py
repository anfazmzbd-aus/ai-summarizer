from unittest.mock import Mock, patch

import pytest

from app.providers.config import ProviderType
from app.providers.factory import ProviderFactory
from app.providers.runtime import ProviderRuntime
from app.providers.settings import ProviderSettings


def test_from_settings_creates_mock_runtime():
    factory = ProviderFactory()

    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="settings-model",
    )

    runtime = ProviderRuntime.from_settings(
        settings,
        factory=factory,
    )

    assert runtime.provider_type is ProviderType.MOCK
    assert runtime.provider_name == "mock"
    assert runtime.service is not None


def test_from_settings_preserves_mock_model():
    factory = ProviderFactory()

    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="custom-model",
    )

    runtime = ProviderRuntime.from_settings(
        settings,
        factory=factory,
    )

    assert runtime._config.model == "custom-model"


def test_from_settings_creates_openai_runtime():
    factory = ProviderFactory()

    settings = ProviderSettings(
        provider=ProviderType.OPENAI,
        model="gpt-5-mini",
        api_key="test-key",
        endpoint="https://example.test",
        organization="test-org",
        timeout=30.0,
        max_retries=1,
    )

    with patch("app.providers.openai.provider.OpenAITransport") as transport_class:
        transport_class.return_value = Mock()

        runtime = ProviderRuntime.from_settings(
            settings,
            factory=factory,
        )

    assert runtime.provider_type is ProviderType.OPENAI
    assert runtime._config.model == "gpt-5-mini"
    assert runtime._config.api_key == "test-key"
    assert runtime._config.endpoint == ("https://example.test")
    assert runtime._config.organization == "test-org"
    assert runtime._config.timeout == 30.0
    assert runtime._config.max_retries == 1


def test_from_settings_requires_openai_api_key():
    factory = ProviderFactory()

    settings = ProviderSettings(
        provider=ProviderType.OPENAI,
        model="gpt-5",
        api_key=None,
    )

    with pytest.raises(
        ValueError,
        match="OpenAI API key cannot be empty",
    ):
        ProviderRuntime.from_settings(
            settings,
            factory=factory,
        )
