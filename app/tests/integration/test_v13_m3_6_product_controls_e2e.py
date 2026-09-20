"""V13 M3.6 product-control end-to-end certification tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

SOURCE_TEXT = (
    "Artificial intelligence can automate repetitive work, improve "
    "decision support, and help teams analyze large volumes of information."
)


def summarize(**overrides: object):
    payload: dict[str, object] = {
        "text": SOURCE_TEXT,
        "provider": "fake",
        "model": "demo",
    }
    payload.update(overrides)

    return client.post("/api/v1/summarize", json=payload)


def test_legacy_request_remains_backward_compatible() -> None:
    response = summarize()

    assert response.status_code == 200

    payload = response.json()

    assert "summary" in payload
    assert payload["summary"]


def test_general_summary_type_is_accepted() -> None:
    response = summarize(summary_type="general")

    assert response.status_code == 200


def test_executive_summary_type_is_accepted() -> None:
    response = summarize(summary_type="executive")

    assert response.status_code == 200


def test_key_points_summary_type_is_accepted() -> None:
    response = summarize(summary_type="key_points")

    assert response.status_code == 200


def test_action_items_summary_type_is_accepted() -> None:
    response = summarize(summary_type="action_items")

    assert response.status_code == 200


def test_findings_summary_type_is_accepted() -> None:
    response = summarize(summary_type="findings")

    assert response.status_code == 200


def test_insights_summary_type_is_accepted() -> None:
    response = summarize(summary_type="insights")

    assert response.status_code == 200


def test_technical_summary_type_is_accepted() -> None:
    response = summarize(summary_type="technical")

    assert response.status_code == 200


def test_short_summary_length_is_accepted() -> None:
    response = summarize(summary_length="short")

    assert response.status_code == 200


def test_medium_summary_length_is_accepted() -> None:
    response = summarize(summary_length="medium")

    assert response.status_code == 200


def test_detailed_summary_length_is_accepted() -> None:
    response = summarize(summary_length="detailed")

    assert response.status_code == 200


def test_custom_instructions_are_accepted() -> None:
    response = summarize(instructions="Focus on operational implications.")

    assert response.status_code == 200


def test_whitespace_instructions_are_accepted_as_empty() -> None:
    response = summarize(instructions="   ")

    assert response.status_code == 200


def test_combined_product_controls_are_accepted() -> None:
    response = summarize(
        summary_type="executive",
        summary_length="short",
        instructions="Focus on decisions and risks.",
    )

    assert response.status_code == 200

    payload = response.json()

    assert "summary" in payload
    assert payload["summary"]


def test_invalid_summary_type_is_rejected() -> None:
    response = summarize(summary_type="unsupported")

    assert response.status_code == 422


def test_invalid_summary_length_is_rejected() -> None:
    response = summarize(summary_length="unsupported")

    assert response.status_code == 422


def test_instruction_limit_is_enforced() -> None:
    response = summarize(instructions="x" * 2001)

    assert response.status_code == 422


def test_instruction_boundary_is_accepted() -> None:
    response = summarize(instructions="x" * 2000)

    assert response.status_code == 200
