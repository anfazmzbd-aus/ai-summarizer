"""
Runtime dependency factory.
"""

from __future__ import annotations

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
    AIRuntimeService,
    SummarizationService,
)

from app.ai import (
    OpenAIConfig,
    OpenAIProvider,
)
from app.config.ai_settings import AISettings


class FakeProvider(AIProvider):

    @property
    def name(self):

        return "fake"

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:

        return AIResponse(
            text=f"Summary: {request.prompt[:40]}",
            model=request.model,
            prompt_tokens=20,
            completion_tokens=30,
        )


def build_summarization_service() -> SummarizationService:

    prompt_registry = PromptRegistry()

    prompt_registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize the following text:\n\n{text}",
        )
    )

    settings = AISettings()
    providers = AIProviderRegistry()

    if settings.provider.lower() == "openai":

        providers.register(
            OpenAIProvider(
                OpenAIConfig(
                    api_key=settings.api_key,
                    model=settings.model,
                    base_url=settings.base_url,
                    organization=settings.organization,
                )
            )
        )

    else:

        providers.register(FakeProvider())

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(providers),
    )

    return SummarizationService(runtime)
