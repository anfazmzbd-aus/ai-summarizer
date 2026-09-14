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
            version="2.0.0",
            template=(
                "You are a professional summarization assistant.\n"
                "Produce an accurate summary of the supplied source.\n"
                "Preserve important facts and do not introduce unsupported "
                "information.\n\n"
                "Summary objective:\n{summary_instruction}\n\n"
                "Length:\n{length_instruction}\n\n"
                "Additional user guidance:\n{additional_instruction}\n\n"
                "Source:\n{text}"
            ),
        )
    )

    settings = AISettings()
    providers = AIProviderRegistry()

    if settings.provider.lower() == "openai":
        if not settings.api_key.strip():
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")

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

    elif settings.provider.lower() == "fake":
        providers.register(FakeProvider())

    else:
        raise ValueError(f"unsupported AI provider: {settings.provider}")

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(providers),
    )

    return SummarizationService(runtime)
