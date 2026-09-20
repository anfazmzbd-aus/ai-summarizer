"""V13 M3.2 summary type control integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def get_html() -> str:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def get_stylesheet() -> str:
    response = TestClient(app).get("/static/style.css")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def test_summary_type_control_exists() -> None:
    html = get_html()

    assert 'id="summaryType"' in html
    assert 'name="summary_type"' in html


def test_summary_type_uses_native_select() -> None:
    html = get_html()

    assert "<select\n" in html
    assert 'id="summaryType"' in html


def test_summary_type_has_accessible_label() -> None:
    html = get_html()

    assert 'for="summaryType"' in html


def test_summary_type_has_help_relationship() -> None:
    html = get_html()

    assert 'aria-describedby="summaryTypeHelp"' in html
    assert 'id="summaryTypeHelp"' in html


def test_summary_type_exposes_general_option() -> None:
    html = get_html()

    assert 'value="general"' in html


def test_summary_type_exposes_executive_option() -> None:
    html = get_html()

    assert 'value="executive"' in html


def test_summary_type_exposes_key_points_option() -> None:
    html = get_html()

    assert 'value="key_points"' in html


def test_summary_type_exposes_action_items_option() -> None:
    html = get_html()

    assert 'value="action_items"' in html


def test_summary_type_exposes_findings_option() -> None:
    html = get_html()

    assert 'value="findings"' in html


def test_summary_type_exposes_insights_option() -> None:
    html = get_html()

    assert 'value="insights"' in html


def test_summary_type_exposes_technical_option() -> None:
    html = get_html()

    assert 'value="technical"' in html


def test_general_is_default_summary_type() -> None:
    html = get_html()

    general_start = html.index('<option value="general"')
    general_end = html.index("</option>", general_start)

    general_option = html[general_start:general_end]

    assert "selected" in general_option


def test_summary_options_have_layout_rule() -> None:
    stylesheet = get_stylesheet()

    assert ".summary-options {" in stylesheet


def test_summary_select_has_focus_visible_rule() -> None:
    stylesheet = get_stylesheet()

    assert ".form-field select:focus-visible {" in stylesheet
