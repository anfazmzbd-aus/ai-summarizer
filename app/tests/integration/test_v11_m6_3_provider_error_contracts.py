import pytest

from app.ai import (
    AIProviderRegistry,
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
from fastapi.testclient import TestClient

from app.main import app
import app.routes.ai as ai_routes

import app.api.dependencies as dependencies
from app.config.ai_settings import AISettings


def _build_service_with_no_registered_providers() -> SummarizationService:
    prompt_registry = PromptRegistry()

    prompt_registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize the following text:\n\n{text}",
        )
    )

    providers = AIProviderRegistry()

    runtime = AIRuntimeService(
        PromptEngine(
            prompt_registry,
            PromptRenderer(),
        ),
        LLMClient(providers),
    )

    return SummarizationService(runtime)


@pytest.mark.anyio
async def test_unknown_provider_fails_at_provider_selection_boundary() -> None:
    application = SummarizationApplication(
        service=_build_service_with_no_registered_providers(),
        pipeline=build_summarization_pipeline_adapter(),
    )

    with pytest.raises(KeyError) as exc_info:
        await application.summarize(
            SummarizationApplicationRequest(
                text="Provider selection must fail closed.",
                provider="missing-provider",
                model="m6-model",
            )
        )

    assert exc_info.value.args == ("missing-provider",)


def test_unknown_provider_is_projected_as_product_safe_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application = SummarizationApplication(
        service=_build_service_with_no_registered_providers(),
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
            "text": "Provider selection must fail safely.",
            "provider": "missing-provider",
            "model": "m6-model",
        },
    )

    assert response.json() == {
        "detail": {
            "error": {
                "code": "SUMMARIZATION_FAILED",
                "message": "summarization could not be completed",
            }
        }
    }

    assert response.status_code == 500
    assert "missing-provider" not in response.text
    assert "KeyError" not in response.text


def test_configured_unsupported_provider_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class UnsupportedProviderSettings:
        provider = "unsupported-provider"
        api_key = ""
        model = "m6-model"
        base_url = None
        organization = None

    monkeypatch.setattr(
        dependencies,
        "AISettings",
        lambda: UnsupportedProviderSettings(),
    )

    with pytest.raises(
        ValueError,
        match="unsupported-provider",
    ):
        dependencies.build_summarization_service()


def test_openai_configuration_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class OpenAISettingsWithoutApiKey:
        provider = "openai"
        api_key = ""
        model = "m6-model"
        base_url = None
        organization = None

    monkeypatch.setattr(
        dependencies,
        "AISettings",
        lambda: OpenAISettingsWithoutApiKey(),
    )

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY",
    ):
        dependencies.build_summarization_service()


def test_ai_settings_reads_environment_at_instance_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "AI_PROVIDER",
        "openai",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "m6-test-key",
    )
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "m6-test-model",
    )

    settings = AISettings()

    assert settings.provider == "openai"
    assert settings.api_key == "m6-test-key"
    assert settings.model == "m6-test-model"
