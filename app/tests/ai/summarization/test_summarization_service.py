import pytest

from app.ai import (
    AIProvider,
    AIProviderRegistry,
    AIRequest,
    AIResponse,
    PromptEngine,
    PromptRegistry,
    PromptRenderer,
    PromptTemplate,
    LLMClient,
    # AIRuntimeRequest,
    AIRuntimeService,
    SummarizationRequest,
    SummarizationService,
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
            text="Short summary",
            model=request.model,
            prompt_tokens=12,
            completion_tokens=18,
        )


@pytest.mark.anyio
async def test_summarization_service():

    prompt_registry = PromptRegistry()

    prompt_registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize:\n\n{text}",
        )
    )

    provider_registry = AIProviderRegistry()
    provider_registry.register(FakeProvider())

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(
            provider_registry,
        ),
    )

    service = SummarizationService(
        runtime,
    )

    result = await service.summarize(
        SummarizationRequest(
            text="Long document",
            provider="fake",
            model="demo",
        )
    )

    assert result.summary == "Short summary"
    assert result.total_tokens == 30
    assert "Long document" in result.prompt
