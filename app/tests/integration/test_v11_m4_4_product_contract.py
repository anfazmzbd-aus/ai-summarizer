"""V11 M4.4 canonical response, metadata, and error contract tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

import app.routes.ai as ai_routes
from app.api.application import ApplicationReviewRequiredError
from app.core.application_contracts import SummarizationApplicationResult
from app.core.application_metadata import SummarizationExecutionMetadata
from app.main import app


class FixedApplication:
    def __init__(self, result: SummarizationApplicationResult) -> None:
        self.result = result

    async def summarize(self, request) -> SummarizationApplicationResult:
        return self.result


def _result(
    metadata: SummarizationExecutionMetadata | None = None,
) -> SummarizationApplicationResult:
    return SummarizationApplicationResult(
        summary="A safe product summary.",
        model="contract-model",
        prompt_tokens=11,
        completion_tokens=4,
        metadata=metadata or SummarizationExecutionMetadata(),
    )


def test_success_projects_product_fields_and_read_only_metadata(monkeypatch) -> None:
    metadata = SummarizationExecutionMetadata(
        strategy="map_reduce",
        chunk_count=3,
        intelligence_mode="preserve",
        trace_id="trace-123",
        explainability_summary="execution remains unchanged",
        attributes={
            "intelligence_observability_status": "normal",
            "intelligence_diagnostic_code": "INTELLIGENCE_NORMAL",
            "intelligence_diagnostic_message": "safe default",
            "provider_secret": "must-not-cross-boundary",
        },
    )
    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: FixedApplication(_result(metadata)),
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={"text": "A contract test.", "provider": "fake", "model": "request-model"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": "A safe product summary.",
        "model": "contract-model",
        "prompt_tokens": 11,
        "completion_tokens": 4,
        "total_tokens": 15,
        "metadata": {
            "strategy": "map_reduce",
            "chunk_count": 3,
            "intelligence_mode": "preserve",
            "trace_id": "trace-123",
            "explainability_summary": "execution remains unchanged",
            "observability_status": "normal",
            "diagnostic_code": "INTELLIGENCE_NORMAL",
            "diagnostic_message": "safe default",
        },
    }
    assert "provider_secret" not in response.text


def test_optional_metadata_absence_is_safe(monkeypatch) -> None:
    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: FixedApplication(_result()),
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={"text": "No metadata details.", "provider": "fake", "model": "demo"},
    )

    assert response.status_code == 200
    assert response.json()["metadata"] == {
        "strategy": None,
        "chunk_count": None,
        "intelligence_mode": None,
        "trace_id": None,
        "explainability_summary": None,
        "observability_status": None,
        "diagnostic_code": None,
        "diagnostic_message": None,
    }


def test_review_is_a_stable_non_execution_product_error(monkeypatch) -> None:
    class ReviewApplication:
        async def summarize(self, request):
            raise ApplicationReviewRequiredError("internal review detail")

    monkeypatch.setattr(ai_routes, "build_summarization_application", ReviewApplication)

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={"text": "Review this request.", "provider": "fake", "model": "demo"},
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
    assert "internal review detail" not in response.text


def test_invalid_authority_is_mapped_without_leaking_internal_error(
    monkeypatch,
) -> None:
    class InvalidApplication:
        async def summarize(self, request):
            raise ValueError("secret authority state")

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        InvalidApplication,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={"text": "Invalid authority.", "provider": "fake", "model": "demo"},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["error"]["code"] == "INVALID_APPLICATION_STATE"
    assert "secret authority state" not in response.text


def test_pipeline_failure_is_mapped_without_leaking_internal_error(monkeypatch) -> None:
    class FailingApplication:
        async def summarize(self, request):
            raise RuntimeError("provider stack trace secret")

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        FailingApplication,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={"text": "Failure boundary.", "provider": "fake", "model": "demo"},
    )

    assert response.status_code == 500
    assert response.json()["detail"]["error"] == {
        "code": "SUMMARIZATION_FAILED",
        "message": "summarization could not be completed",
    }
    assert "provider stack trace secret" not in response.text


def test_compatibility_endpoint_remains_separate() -> None:
    response = TestClient(app).post(
        "/summarize",
        json={"text": "Compatibility behavior remains separate."},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "summary" in response.json()["result"]
