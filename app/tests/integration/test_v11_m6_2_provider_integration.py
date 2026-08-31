import pytest

from app.ai import (
    AIProvider,
    AIProviderRegistry,
    AIRequest,
    AIResponse,
    AIRuntimeService,
    LLMClient,
    PromptEngine,
    PromptRegistry,
    PromptRenderer,
    PromptTemplate,
    SummarizationService,
)
from app.api.application import SummarizationApplication
from app.core.application_contracts import SummarizationApplicationRequest
from app.core.summarization_pipeline_factory import (
    build_summarization_pipeline_adapter,
)


class DeterministicProvider(AIProvider):
    @property
    def name(self) -> str:
        return "m6-test-provider"

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        return AIResponse(
            text="M6 deterministic provider summary.",
            model=request.model,
            prompt_tokens=11,
            completion_tokens=7,
        )


def _build_provider_backed_service() -> SummarizationService:
    prompt_registry = PromptRegistry()

    prompt_registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize the following text:\n\n{text}",
        )
    )

    providers = AIProviderRegistry()
    providers.register(DeterministicProvider())

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(providers),
    )

    return SummarizationService(runtime)


@pytest.mark.anyio
async def test_canonical_application_executes_through_provider_boundary() -> None:
    application = SummarizationApplication(
        service=_build_provider_backed_service(),
        pipeline=build_summarization_pipeline_adapter(),
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text=(
                "Artificial intelligence can help teams summarize "
                "operational information while preserving human oversight."
            ),
            provider="m6-test-provider",
            model="m6-provider-model",
        )
    )

    assert result.summary == "M6 deterministic provider summary."
    assert result.model == "m6-provider-model"
    assert result.prompt_tokens == 11
    assert result.completion_tokens == 7
    assert result.total_tokens == 18


class AlternateDeterministicProvider(AIProvider):
    @property
    def name(self) -> str:
        return "m6-alternate-provider"

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        return AIResponse(
            text="Alternate provider summary.",
            model=request.model,
            prompt_tokens=13,
            completion_tokens=4,
        )


@pytest.mark.anyio
async def test_canonical_application_honors_requested_provider_selection() -> None:
    prompt_registry = PromptRegistry()
    prompt_registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize the following text:\n\n{text}",
        )
    )

    providers = AIProviderRegistry()
    providers.register(DeterministicProvider())
    providers.register(AlternateDeterministicProvider())

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(providers),
    )

    application = SummarizationApplication(
        service=SummarizationService(runtime),
        pipeline=build_summarization_pipeline_adapter(),
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="Provider routing should remain deterministic and explicit.",
            provider="m6-alternate-provider",
            model="m6-alternate-model",
        )
    )

    assert result.summary == "Alternate provider summary."
    assert result.model == "m6-alternate-model"
    assert result.prompt_tokens == 13
    assert result.completion_tokens == 4
    assert result.total_tokens == 17
