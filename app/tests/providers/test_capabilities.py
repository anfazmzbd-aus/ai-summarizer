from app.providers.capabilities import (
    ProviderCapabilities,
)


def test_default_capabilities():

    capabilities = ProviderCapabilities()

    assert capabilities.streaming is False
    assert capabilities.vision is False


def test_enabled_capability():

    capabilities = ProviderCapabilities(
        tool_calling=True,
        reasoning=True,
    )

    assert capabilities.tool_calling is True
    assert capabilities.reasoning is True
