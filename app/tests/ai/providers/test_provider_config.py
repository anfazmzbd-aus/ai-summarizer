from app.ai import (
    ProviderConfig,
    ProviderType,
)


def test_provider_config():

    config = ProviderConfig(
        provider=ProviderType.OPENAI,
        model="gpt-model",
        api_key="test",
    )

    assert config.model == "gpt-model"
    assert config.api_key == "test"
