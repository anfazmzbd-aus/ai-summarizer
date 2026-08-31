"""V11 M5.5 long-document metadata and failure contracts."""

from fastapi.testclient import TestClient

from app.main import app

import app.routes.ai as ai_routes


def _long_document() -> str:
    paragraph = (
        "Artificial intelligence systems support organizations by analyzing "
        "large amounts of information, identifying patterns, assisting with "
        "routine decisions, and helping teams summarize complex operational "
        "data. Human oversight remains important when systems affect business "
        "processes, customers, or other consequential decisions. "
    )

    return "\n\n".join(paragraph for _ in range(1400))


def test_long_document_response_exposes_only_product_safe_metadata() -> None:
    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": _long_document(),
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    metadata = payload["metadata"]

    assert metadata["strategy"] == "hierarchical"
    assert metadata["chunk_count"] == 128
    assert metadata["intelligence_mode"] == "preserve"
    assert metadata["observability_status"] == "normal"

    assert "selection" not in metadata
    assert "execution" not in metadata
    assert "chunks" not in metadata
    assert "pipeline" not in metadata
    assert "planner" not in metadata
    assert "provider_settings" not in metadata


def test_long_document_failure_uses_product_safe_error_contract(
    monkeypatch,
) -> None:
    class FailingApplication:
        async def summarize(self, request):
            raise RuntimeError(
                "internal long-document pipeline failure: secret execution detail"
            )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        FailingApplication,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": _long_document(),
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 500

    assert response.json()["detail"]["error"] == {
        "code": "SUMMARIZATION_FAILED",
        "message": "summarization could not be completed",
    }

    assert "internal long-document pipeline failure" not in response.text
    assert "secret execution detail" not in response.text
