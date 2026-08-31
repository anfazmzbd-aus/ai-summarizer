import pytest
from fastapi.testclient import TestClient

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
from app.core.summarization_pipeline_factory import (
    build_summarization_pipeline_adapter,
)
from app.main import app

import app.routes.ai as ai_routes

import asyncio

from app.ai.client import LLMOptions


class FailingProvider(AIProvider):
    @property
    def name(self) -> str:
        return "m6-failing-provider"

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        raise RuntimeError("internal provider failure: secret diagnostic")


def _build_failing_provider_service() -> SummarizationService:
    prompt_registry = PromptRegistry()

    prompt_registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize the following text:\n\n{text}",
        )
    )

    providers = AIProviderRegistry()
    providers.register(FailingProvider())

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(providers),
    )

    return SummarizationService(runtime)


def test_provider_failure_is_projected_as_product_safe_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application = SummarizationApplication(
        service=_build_failing_provider_service(),
        pipeline=build_summarization_pipeline_adapter(),
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Provider failures must remain product safe.",
            "provider": "m6-failing-provider",
            "model": "m6-model",
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": {
            "error": {
                "code": "SUMMARIZATION_FAILED",
                "message": "summarization could not be completed",
            }
        }
    }

    assert "internal provider failure" not in response.text
    assert "secret diagnostic" not in response.text
    assert "RuntimeError" not in response.text


class SlowProvider(AIProvider):
    @property
    def name(self) -> str:
        return "m6-slow-provider"

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        await asyncio.sleep(0.05)

        return AIResponse(
            text="This response should never complete.",
            model=request.model,
            prompt_tokens=1,
            completion_tokens=1,
        )


def _build_slow_provider_service() -> SummarizationService:
    prompt_registry = PromptRegistry()

    prompt_registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize the following text:\n\n{text}",
        )
    )

    providers = AIProviderRegistry()
    providers.register(SlowProvider())

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(
            providers,
            options=LLMOptions(
                timeout_seconds=0.001,
            ),
        ),
    )

    return SummarizationService(runtime)


def test_provider_timeout_is_projected_as_product_safe_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application = SummarizationApplication(
        service=_build_slow_provider_service(),
        pipeline=build_summarization_pipeline_adapter(),
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Provider timeout behavior must remain product safe.",
            "provider": "m6-slow-provider",
            "model": "m6-model",
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": {
            "error": {
                "code": "SUMMARIZATION_FAILED",
                "message": "summarization could not be completed",
            }
        }
    }

    assert "timed out" not in response.text.lower()
    assert "LLMTimeoutError" not in response.text


class MalformedProvider(AIProvider):
    @property
    def name(self) -> str:
        return "m6-malformed-provider"

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        return None  # type: ignore[return-value]


def _build_malformed_provider_service() -> SummarizationService:
    prompt_registry = PromptRegistry()

    prompt_registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize the following text:\n\n{text}",
        )
    )

    providers = AIProviderRegistry()
    providers.register(MalformedProvider())

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(providers),
    )

    return SummarizationService(runtime)


def test_malformed_provider_response_is_projected_as_product_safe_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application = SummarizationApplication(
        service=_build_malformed_provider_service(),
        pipeline=build_summarization_pipeline_adapter(),
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Malformed provider output must fail safely.",
            "provider": "m6-malformed-provider",
            "model": "m6-model",
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": {
            "error": {
                "code": "SUMMARIZATION_FAILED",
                "message": "summarization could not be completed",
            }
        }
    }

    assert "NoneType" not in response.text
    assert "AttributeError" not in response.text
