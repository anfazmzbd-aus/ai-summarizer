"""V11 M4.5 end-to-end intelligence authority scenarios."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

import app.routes.ai as ai_routes
from app.ai import SummarizationResponse
from app.api.application import SummarizationApplication
from app.core.intelligence_integration import ApplicationIntelligenceResult
from app.core.summarization_pipeline_factory import (
    build_summarization_pipeline_adapter,
)
from app.main import app


class RecordingSummarizationService:
    def __init__(self) -> None:
        self.requests = []

    async def summarize(self, request) -> SummarizationResponse:
        self.requests.append(request)
        return SummarizationResponse(
            summary="Deterministic preserve summary.",
            prompt="Deterministic test prompt.",
            model=request.model or "demo",
            prompt_tokens=12,
            completion_tokens=5,
        )


class FixedIntelligenceBoundary:
    def __init__(self, result: ApplicationIntelligenceResult) -> None:
        self.result = result
        self.requests = []

    def evaluate(self, request) -> ApplicationIntelligenceResult:
        self.requests.append(request)
        return self.result


def _intelligence_result(
    *,
    mode: str,
    execution_change_authorized: bool = False,
    bounded_constraint_required: bool = False,
    review_required: bool = False,
) -> ApplicationIntelligenceResult:
    context_id = uuid4()

    return ApplicationIntelligenceResult(
        context_id=context_id,
        correlation_id=uuid4(),
        action="summarize",
        mode=mode,
        execution_change_authorized=execution_change_authorized,
        bounded_constraint_required=bounded_constraint_required,
        review_required=review_required,
        reasons=(f"{mode} authority scenario",),
        trace_id=str(context_id),
        explainability_summary=f"{mode} authority scenario",
        observability_status=mode,
        diagnostic_code=f"INTELLIGENCE_{mode.upper()}",
        diagnostic_message=f"{mode} authority scenario",
        reason_count=1,
    )


def test_preserve_executes_through_canonical_product_path(monkeypatch) -> None:
    service = RecordingSummarizationService()
    intelligence = FixedIntelligenceBoundary(
        _intelligence_result(mode="preserve"),
    )

    application = SummarizationApplication(
        service=service,
        pipeline=build_summarization_pipeline_adapter(),
        intelligence=intelligence,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": "Artificial intelligence can assist software teams by "
            "summarizing large amounts of technical information.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["summary"] == "Deterministic preserve summary."
    assert payload["metadata"]["intelligence_mode"] == "preserve"
    assert payload["metadata"]["observability_status"] == "preserve"
    assert payload["metadata"]["diagnostic_code"] == "INTELLIGENCE_PRESERVE"

    assert len(intelligence.requests) == 1
    assert len(service.requests) == 1


def test_advisory_executes_without_changing_product_flow(monkeypatch) -> None:
    service = RecordingSummarizationService()
    intelligence = FixedIntelligenceBoundary(
        _intelligence_result(mode="advisory"),
    )

    application = SummarizationApplication(
        service=service,
        pipeline=build_summarization_pipeline_adapter(),
        intelligence=intelligence,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": "Operational teams use structured incident reviews to "
            "identify recurring issues and improve service reliability.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["summary"] == "Deterministic preserve summary."
    assert payload["metadata"]["intelligence_mode"] == "advisory"
    assert payload["metadata"]["observability_status"] == "advisory"
    assert payload["metadata"]["diagnostic_code"] == "INTELLIGENCE_ADVISORY"

    assert len(intelligence.requests) == 1
    assert len(service.requests) == 1


def test_review_stops_execution_and_returns_product_error(monkeypatch) -> None:
    service = RecordingSummarizationService()
    intelligence = FixedIntelligenceBoundary(
        _intelligence_result(
            mode="review",
            review_required=True,
        ),
    )

    application = SummarizationApplication(
        service=service,
        pipeline=build_summarization_pipeline_adapter(),
        intelligence=intelligence,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": "This request requires intelligence review before execution.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": {
            "error": {
                "code": "REVIEW_REQUIRED",
                "message": "summarization requires review before execution",
            }
        }
    }

    assert len(intelligence.requests) == 1
    assert len(service.requests) == 0


def test_constrained_executes_only_with_bounded_authority(monkeypatch) -> None:
    service = RecordingSummarizationService()
    intelligence = FixedIntelligenceBoundary(
        _intelligence_result(
            mode="constrained",
            execution_change_authorized=True,
            bounded_constraint_required=True,
        ),
    )

    application = SummarizationApplication(
        service=service,
        pipeline=build_summarization_pipeline_adapter(),
        intelligence=intelligence,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": "A bounded intelligence decision may authorize a constrained "
            "execution change while preserving the existing pipeline boundary.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["summary"] == "Deterministic preserve summary."
    assert payload["metadata"]["intelligence_mode"] == "constrained"
    assert payload["metadata"]["observability_status"] == "constrained"
    assert payload["metadata"]["diagnostic_code"] == "INTELLIGENCE_CONSTRAINED"

    assert len(intelligence.requests) == 1
    assert len(service.requests) == 1


def test_constrained_without_bounded_authority_fails_closed(monkeypatch) -> None:
    service = RecordingSummarizationService()
    intelligence = FixedIntelligenceBoundary(
        _intelligence_result(
            mode="constrained",
            execution_change_authorized=True,
            bounded_constraint_required=False,
        ),
    )

    application = SummarizationApplication(
        service=service,
        pipeline=build_summarization_pipeline_adapter(),
        intelligence=intelligence,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": "An invalid constrained authority state must fail closed.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "error": {
                "code": "INVALID_APPLICATION_STATE",
                "message": "summarization could not be authorized",
            }
        }
    }

    assert len(intelligence.requests) == 1
    assert len(service.requests) == 0
