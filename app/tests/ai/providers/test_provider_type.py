from app.ai import ProviderType


def test_provider_type():

    assert ProviderType.OPENAI.value == "openai"
