import pytest

from app.ai import (
    AIProvider,
    AIProviderRegistry,
    AIRequest,
    AIResponse,
    LLMClient,
)


class FakeProvider(AIProvider):

    @property
    def name(self):

        return "fake"

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:

        return AIResponse(
            text="generated",
            model=request.model,
        )


@pytest.mark.anyio
async def test_client():

    registry = AIProviderRegistry()

    registry.register(FakeProvider())

    client = LLMClient(
        registry,
    )

    response = await client.generate(
        "fake",
        AIRequest(
            prompt="Hello",
            model="demo",
        ),
    )

    assert response.text == "generated"
