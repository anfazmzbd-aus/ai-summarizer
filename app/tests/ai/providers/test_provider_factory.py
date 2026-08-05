from app.ai import (
    ProviderFactory,
    ProviderType,
)


def test_factory():

    factory = ProviderFactory()

    config = factory.create_config(
        ProviderType.OPENAI,
        "demo",
    )

    assert config.provider == ProviderType.OPENAI
    assert config.model == "demo"
