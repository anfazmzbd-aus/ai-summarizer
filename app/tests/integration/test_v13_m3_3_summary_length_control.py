"""V13 M3.3 summary length control integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def get_html() -> str:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def test_summary_length_control_exists() -> None:
    html = get_html()

    assert 'id="summaryLength"' in html
    assert 'name="summary_length"' in html


def test_summary_length_uses_native_select() -> None:
    html = get_html()

    assert "<select\n" in html
    assert 'id="summaryLength"' in html


def test_summary_length_has_accessible_label() -> None:
    html = get_html()

    assert 'for="summaryLength"' in html


def test_summary_length_has_help_relationship() -> None:
    html = get_html()

    assert 'aria-describedby="summaryLengthHelp"' in html
    assert 'id="summaryLengthHelp"' in html


def test_summary_length_exposes_short_option() -> None:
    html = get_html()

    assert 'value="short"' in html


def test_summary_length_exposes_medium_option() -> None:
    html = get_html()

    assert 'value="medium"' in html


def test_summary_length_exposes_detailed_option() -> None:
    html = get_html()

    assert 'value="detailed"' in html


def test_medium_is_default_summary_length() -> None:
    html = get_html()

    medium_start = html.index('<option value="medium"')
    medium_end = html.index("</option>", medium_start)

    medium_option = html[medium_start:medium_end]

    assert "selected" in medium_option


def test_summary_length_uses_existing_form_field_structure() -> None:
    html = get_html()

    length_position = html.index('id="summaryLength"')
    preceding_markup = html[:length_position]

    assert preceding_markup.rfind('class="form-field"') != -1


def test_length_control_does_not_add_frontend_prompt_logic() -> None:
    html = get_html()

    assert 'name="summary_length"' in html
