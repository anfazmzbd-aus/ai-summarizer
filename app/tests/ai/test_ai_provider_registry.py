from app.ai import (
    AIProvider,
    AIProviderRegistry,
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
            text="ok",
            model=request.model,
        )


def test_registry():

    registry = AIProviderRegistry()

    registry.register(FakeProvider())

    assert registry.names() == ["fake"]

    assert registry.get("fake").name == "fake"
