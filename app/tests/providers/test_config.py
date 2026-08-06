from app.providers.config import (
    ProviderConfig,
    ProviderType,
)


def test_provider_config_defaults():
    config = ProviderConfig(
        provider=ProviderType.MOCK,
        model="mock-model",
    )

    assert config.provider is ProviderType.MOCK
    assert config.model == "mock-model"
    assert config.timeout == 60.0
    assert config.max_retries == 3
    assert config.verify_ssl is True
