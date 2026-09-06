"""V12 production certification for the public summarization boundary."""

from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.routes.ai as ai_routes
from app.routes.ai import router


class StubApplication:
    def __init__(self) -> None:
        self.requests = []

    async def summarize(self, request):
        self.requests.append(request)

        return SimpleNamespace(
            summary="certified summary",
            model=request.model,
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            metadata=SimpleNamespace(
                strategy="direct",
                chunk_count=1,
                intelligence_mode="preserve",
                trace_id="v12-certification-trace",
                explainability_summary="execution preserved",
                attributes={
                    "intelligence_observability_status": "normal",
                    "intelligence_diagnostic_code": "INTELLIGENCE_NORMAL",
                    "intelligence_diagnostic_message": "normal execution",
                    "recovery_occurred": "false",
                    "recovery_action": "",
                    "recovery_strategy": "",
                },
            ),
        )


def _client(monkeypatch):
    application = StubApplication()

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    app = FastAPI()
    app.include_router(router)

    return TestClient(app), application


def test_missing_text_is_rejected_before_application_execution(monkeypatch) -> None:
    client, application = _client(monkeypatch)

    response = client.post(
        "/api/v1/summarize",
        json={
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 422
    assert application.requests == []


def test_empty_text_is_rejected_before_application_execution(monkeypatch) -> None:
    client, application = _client(monkeypatch)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 422
    assert application.requests == []


def test_whitespace_only_text_is_rejected_before_application_execution(
    monkeypatch,
) -> None:
    client, application = _client(monkeypatch)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "   \t\n",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 422
    assert application.requests == []


def test_valid_text_is_preserved_without_rewriting(monkeypatch) -> None:
    client, application = _client(monkeypatch)

    source_text = "  Preserve intentional surrounding whitespace.  "

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": source_text,
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200
    assert len(application.requests) == 1
    assert application.requests[0].text == source_text


def test_public_provider_and_model_defaults_are_preserved(monkeypatch) -> None:
    client, application = _client(monkeypatch)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Production certification input.",
        },
    )

    assert response.status_code == 200

    assert len(application.requests) == 1
    assert application.requests[0].provider == "fake"
    assert application.requests[0].model == "demo"


def test_public_boundary_projects_only_supported_request_fields(monkeypatch) -> None:
    client, application = _client(monkeypatch)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Production certification input.",
            "provider": "fake",
            "model": "demo",
            "unexpected_internal_option": "must-not-cross-boundary",
        },
    )

    assert response.status_code == 200

    assert len(application.requests) == 1

    request = application.requests[0]

    assert request.text == "Production certification input."
    assert request.provider == "fake"
    assert request.model == "demo"
    assert not hasattr(request, "unexpected_internal_option")
