from app.providers.capabilities import (
    ProviderCapabilities,
)

from app.providers.provider_info import (
    ProviderInfo,
)


def test_provider_info():

    info = ProviderInfo(
        name="openai",
        default_model="gpt-model",
        models=("gpt-model",),
        capabilities=ProviderCapabilities(),
    )

    assert info.name == "openai"
    assert info.default_model == "gpt-model"
