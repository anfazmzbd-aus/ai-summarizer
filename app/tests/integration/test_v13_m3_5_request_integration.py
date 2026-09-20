"""V13 M3.5 product control request integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def get_resource(path: str) -> str:
    response = TestClient(app).get(path)

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def get_request_body() -> str:
    javascript = get_resource("/static/app.js")

    start = javascript.index("body: JSON.stringify({")
    end = javascript.index("}),", start)

    return javascript[start:end]


def test_javascript_references_summary_type_control() -> None:
    javascript = get_resource("/static/app.js")

    assert 'document.getElementById("summaryType")' in javascript


def test_javascript_references_summary_length_control() -> None:
    javascript = get_resource("/static/app.js")

    assert 'document.getElementById("summaryLength")' in javascript


def test_request_sends_source_text() -> None:
    request_body = get_request_body()

    assert "text: normalizedText" in request_body


def test_request_preserves_current_provider_contract() -> None:
    request_body = get_request_body()

    assert 'provider: "fake"' in request_body


def test_request_preserves_current_model_contract() -> None:
    request_body = get_request_body()

    assert 'model: "demo"' in request_body


def test_request_sends_summary_type() -> None:
    request_body = get_request_body()

    assert "summary_type: summaryType.value" in request_body


def test_request_sends_summary_length() -> None:
    request_body = get_request_body()

    assert "summary_length: summaryLength.value" in request_body


def test_request_sends_custom_instructions() -> None:
    request_body = get_request_body()

    assert "instructions: customInstructions.value.trim() || null" in request_body


def test_request_does_not_send_display_labels() -> None:
    request_body = get_request_body()

    assert 'summary_type: "General"' not in request_body
    assert 'summary_length: "Medium"' not in request_body


def test_request_does_not_construct_product_prompt() -> None:
    request_body = get_request_body()

    assert "prompt:" not in request_body
    assert "prompt_name:" not in request_body


def test_request_does_not_send_pipeline_intent() -> None:
    request_body = get_request_body()

    assert "intent:" not in request_body


def test_instructions_are_normalized_at_submission_boundary() -> None:
    request_body = get_request_body()

    assert ".trim()" in request_body
    assert "|| null" in request_body
