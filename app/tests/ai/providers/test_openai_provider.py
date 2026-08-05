from app.ai import (
    OpenAIConfig,
    OpenAIProvider,
)


def test_provider_name():

    provider = OpenAIProvider(
        OpenAIConfig(
            api_key="test",
            model="demo",
        )
    )

    assert provider.name == "openai"
