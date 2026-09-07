"""V12 security certification for production-facing boundaries."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.api.dependencies as dependencies
import app.routes.ai as ai_routes
from app.config.ai_settings import AISettings
from app.main import app


def test_ai_settings_repr_does_not_expose_openai_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "v12-super-secret-api-key"

    monkeypatch.setenv("OPENAI_API_KEY", secret)

    settings = AISettings()

    assert settings.api_key == secret
    assert secret not in repr(settings)


def test_openai_api_key_is_available_to_provider_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "v12-provider-construction-key"

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", secret)
    monkeypatch.setenv("OPENAI_MODEL", "v12-certification-model")

    captured = {}

    class StubOpenAIProvider:
        def __init__(self, config) -> None:
            captured["config"] = config

        @property
        def name(self) -> str:
            return "openai"

    monkeypatch.setattr(
        dependencies,
        "OpenAIProvider",
        StubOpenAIProvider,
    )

    dependencies.build_summarization_service()

    assert captured["config"].api_key == secret


def test_missing_openai_api_key_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "   ")

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY",
    ):
        dependencies.build_summarization_service()


def test_unsupported_configured_provider_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "AI_PROVIDER",
        "v12-unsupported-provider",
    )

    with pytest.raises(
        ValueError,
        match="unsupported AI provider",
    ):
        dependencies.build_summarization_service()


def test_provider_exception_secret_is_not_exposed_to_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "v12-provider-secret-detail"

    class FailingApplication:
        async def summarize(self, request):
            raise RuntimeError(f"provider failure containing {secret}")

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: FailingApplication(),
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Security certification input.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 500
    assert secret not in response.text
    assert "RuntimeError" not in response.text

    assert response.json() == {
        "detail": {
            "error": {
                "code": "SUMMARIZATION_FAILED",
                "message": "summarization could not be completed",
            }
        }
    }
