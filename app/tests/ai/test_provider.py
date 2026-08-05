import pytest

from app.ai import (
    AIProvider,
    AIRequest,
    AIResponse,
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
            text="summary",
            model=request.model,
        )


@pytest.mark.anyio
async def test_provider():

    provider = FakeProvider()

    response = await provider.generate(
        AIRequest(
            prompt="Hello",
            model="demo",
        )
    )

    assert response.text == "summary"
