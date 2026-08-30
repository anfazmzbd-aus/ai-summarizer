"""V11 M4.2 supported frontend to canonical API integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_supported_frontend_entry_point_is_mounted() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert 'id="summaryForm"' in response.text
    assert 'src="/static/app.js"' in response.text


def test_supported_frontend_uses_canonical_summarization_endpoint() -> None:
    response = TestClient(app).get("/static/app.js")

    assert response.status_code == 200
    assert 'fetch("/api/v1/summarize"' in response.text
    assert 'fetch("/summarize"' not in response.text


def test_supported_frontend_static_stylesheet_remains_available() -> None:
    response = TestClient(app).get("/static/style.css")

    assert response.status_code == 200
    assert ".container" in response.text
