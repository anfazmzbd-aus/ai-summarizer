import pytest

from app.ai import (
    AIProvider,
    AIProviderRegistry,
    AIResponse,
    AIRequest,
    PromptEngine,
    PromptRegistry,
    PromptRenderer,
    PromptTemplate,
    LLMClient,
    AIRuntimeRequest,
    AIRuntimeService,
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
async def test_runtime_service():

    prompt_registry = PromptRegistry()

    prompt_registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize {text}",
        )
    )

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(
            AIProviderRegistry(),
        ),
    )

    runtime._client._registry.register(FakeProvider())

    result = await runtime.generate(
        AIRuntimeRequest(
            provider="fake",
            prompt_name="summary",
            model="demo",
            variables={
                "text": "Hello World",
            },
        )
    )

    assert result.prompt == "Summarize Hello World"
    assert result.response.text == "summary"
