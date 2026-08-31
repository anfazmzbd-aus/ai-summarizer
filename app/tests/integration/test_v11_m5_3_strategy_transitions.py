"""V11 M5.3 strategy transition integration."""

from fastapi.testclient import TestClient

from app.main import app


def _post_summary(text: str) -> dict:
    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": text,
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200
    return response.json()


def test_short_document_uses_direct_strategy() -> None:
    payload = _post_summary(
        "Artificial intelligence helps teams automate repetitive tasks "
        "and summarize operational information."
    )

    metadata = payload["metadata"]

    assert metadata["strategy"] == "direct"
    assert metadata["chunk_count"] == 1


def test_medium_document_uses_map_reduce_strategy() -> None:
    paragraph = (
        "Artificial intelligence supports software engineering teams by "
        "assisting with analysis, automation, documentation, testing, and "
        "operational decision support. Human oversight remains important "
        "when automated systems influence production workflows. "
    )

    payload = _post_summary("\n\n".join(paragraph for _ in range(180)))

    metadata = payload["metadata"]

    assert metadata["strategy"] == "map_reduce"
    assert metadata["chunk_count"] > 1


def test_long_document_uses_hierarchical_strategy() -> None:
    paragraph = (
        "Artificial intelligence systems support organizations by analyzing "
        "large amounts of information, identifying patterns, assisting with "
        "routine decisions, and helping teams summarize complex operational "
        "data. Human oversight remains important when systems affect business "
        "processes, customers, or other consequential decisions. "
    )

    payload = _post_summary("\n\n".join(paragraph for _ in range(1400)))

    metadata = payload["metadata"]

    assert metadata["strategy"] == "hierarchical"
    assert metadata["chunk_count"] == 128
