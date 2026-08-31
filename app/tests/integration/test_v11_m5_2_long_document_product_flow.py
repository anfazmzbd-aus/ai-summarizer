"""V11 M5.2 canonical long-document product integration."""

from fastapi.testclient import TestClient

from app.main import app


def _long_document() -> str:
    paragraph = (
        "Artificial intelligence systems support organizations by analyzing "
        "large amounts of information, identifying patterns, assisting with "
        "routine decisions, and helping teams summarize complex operational "
        "data. Human oversight remains important when systems affect business "
        "processes, customers, or other consequential decisions. "
    )

    return "\n\n".join(paragraph for _ in range(1400))


def test_long_document_uses_canonical_product_pipeline() -> None:
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

    assert payload["summary"]
    assert payload["model"] == "demo"

    metadata = payload["metadata"]

    assert metadata["chunk_count"] > 1
    assert metadata["strategy"] == "hierarchical"
    assert metadata["chunk_count"] == 128

    assert metadata["intelligence_mode"] == "preserve"
    assert metadata["observability_status"] == "normal"
