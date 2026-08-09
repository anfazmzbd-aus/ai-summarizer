from app.providers.openai.config import OpenAIConfig
from app.providers.openai.transport import OpenAITransport


def test_transport_creation():

    transport = OpenAITransport(
        OpenAIConfig(
            api_key="test-key",
        )
    )

    assert transport.client is not None
