from app.providers.openai.provider import (
    OpenAIProvider,
)

from app.providers.capabilities import (
    ProviderCapabilities,
)

from app.providers.openai.adapter import (
    OpenAIAdapter,
)


def test_provider_name():

    provider = OpenAIProvider(OpenAIAdapter("client"))

    assert provider.name == "openai"


def test_provider_capabilities():

    provider = OpenAIProvider(OpenAIAdapter("client"))

    capabilities = provider.capabilities()

    assert isinstance(
        capabilities,
        ProviderCapabilities,
    )

    assert capabilities.tool_calling is True
