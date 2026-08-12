from unittest.mock import Mock, patch

from app.providers.config import ProviderType
from app.providers.factory import ProviderFactory
from app.providers.openai.provider import OpenAIProvider
from app.providers.runtime import ProviderRuntime


def test_openai_runtime_registers_openai_provider():
    factory = ProviderFactory()

    with patch("app.providers.openai.provider.OpenAITransport") as transport_class:
        transport_class.return_value = Mock()

        runtime = ProviderRuntime.openai(
            factory,
            api_key="test-key",
            model="gpt-5",
        )

    assert ProviderType.OPENAI in factory.supported_providers()
    assert runtime.provider_type is ProviderType.OPENAI
    assert runtime.provider_name == "openai"


def test_openai_runtime_creates_openai_provider():
    factory = ProviderFactory()

    with patch("app.providers.openai.provider.OpenAITransport") as transport_class:
        transport_class.return_value = Mock()

        runtime = ProviderRuntime.openai(
            factory,
            api_key="test-key",
            model="gpt-5-mini",
        )
    provider = factory.create(
        runtime._config,
    )

    assert isinstance(provider, OpenAIProvider)


def test_openai_runtime_passes_configuration():
    factory = ProviderFactory()

    with patch("app.providers.openai.provider.OpenAITransport") as transport_class:
        transport_class.return_value = Mock()

        ProviderRuntime.openai(
            factory,
            api_key="test-key",
            model="gpt-5-mini",
            organization="test-org",
            endpoint="https://example.test",
            timeout=30.0,
            max_retries=1,
        )

        config = transport_class.call_args.args[0]

    assert config.api_key == "test-key"
    assert config.model == "gpt-5-mini"
    assert config.organization == "test-org"
    assert config.base_url == "https://example.test"
    assert config.timeout == 30.0
    assert config.max_retries == 1


def test_openai_runtime_reuses_existing_factory_registration():
    factory = ProviderFactory()

    creator = Mock()
    factory.register(
        ProviderType.OPENAI,
        creator,
    )

    with patch("app.providers.openai.provider.OpenAITransport") as transport_class:
        runtime = ProviderRuntime.openai(
            factory,
            api_key="test-key",
        )

    assert runtime.provider_type is ProviderType.OPENAI
    assert factory.supported_providers().count(ProviderType.OPENAI) == 1

    transport_class.assert_not_called()


def test_openai_runtime_requires_api_key():
    factory = ProviderFactory()

    try:
        ProviderRuntime.openai(
            factory,
            api_key="",
        )
    except ValueError as exc:
        assert str(exc) == ("OpenAI API key cannot be empty.")
    else:
        raise AssertionError("Expected ValueError for empty OpenAI API key")
