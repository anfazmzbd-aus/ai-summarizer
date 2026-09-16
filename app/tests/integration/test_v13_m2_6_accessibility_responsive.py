"""V13 M2.6 responsive and accessibility certification tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def get_html() -> str:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def get_javascript() -> str:
    response = TestClient(app).get("/static/app.js")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def get_stylesheet() -> str:
    response = TestClient(app).get("/static/style.css")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def test_document_declares_language() -> None:
    html = get_html()

    assert '<html lang="en">' in html


def test_document_has_responsive_viewport() -> None:
    html = get_html()

    assert 'name="viewport"' in html
    assert "width=device-width" in html


def test_source_textarea_has_accessible_label() -> None:
    html = get_html()

    assert 'for="inputText"' in html
    assert 'id="inputText"' in html


def test_submit_control_uses_native_button() -> None:
    html = get_html()

    assert 'id="summarizeButton"' in html
    assert 'type="submit"' in html


def test_processing_status_is_live_region() -> None:
    html = get_html()

    assert 'id="status"' in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert 'aria-atomic="true"' in html


def test_input_metrics_are_accessibly_announced() -> None:
    html = get_html()

    assert 'id="inputMetrics"' in html
    assert 'aria-live="polite"' in html


def test_result_has_semantic_heading_relationship() -> None:
    html = get_html()

    assert 'aria-labelledby="resultHeading"' in html
    assert 'id="resultHeading"' in html


def test_result_summary_is_keyboard_focusable() -> None:
    html = get_html()

    assert 'id="summaryContent"' in html
    assert 'tabindex="0"' in html


def test_processing_details_have_semantic_heading() -> None:
    html = get_html()

    assert 'aria-labelledby="processingDetailsHeading"' in html
    assert 'id="processingDetailsHeading"' in html


def test_metadata_uses_description_list_semantics() -> None:
    html = get_html()

    assert '<dl class="metadata-grid">' in html
    assert "<dt>Strategy</dt>" in html
    assert "<dt>Chunks</dt>" in html
    assert "<dt>Intelligence</dt>" in html
    assert "<dt>Observability</dt>" in html


def test_decorative_status_indicator_is_hidden_from_accessibility_tree() -> None:
    html = get_html()

    assert 'class="result-status-indicator"' in html
    assert 'aria-hidden="true"' in html


def test_javascript_moves_focus_after_success() -> None:
    javascript = get_javascript()

    success_position = javascript.index("setUIState(UI_STATE.SUCCESS);")
    focus_position = javascript.index("summaryContent.focus();")

    assert success_position < focus_position


def test_javascript_does_not_clear_source_after_success() -> None:
    javascript = get_javascript()

    assert 'inputText.value = ""' not in javascript
    assert "inputText.value = ''" not in javascript


def test_loading_state_prevents_duplicate_submission() -> None:
    javascript = get_javascript()

    assert "if (currentState === UI_STATE.LOADING)" in javascript
    assert "currentState === UI_STATE.LOADING ||" in javascript


def test_stylesheet_has_focus_visible_support() -> None:
    stylesheet = get_stylesheet()

    assert ":focus-visible" in stylesheet
    assert ".summary-content:focus-visible" in stylesheet


def test_stylesheet_has_reduced_motion_support() -> None:
    stylesheet = get_stylesheet()

    assert "@media (prefers-reduced-motion: reduce)" in stylesheet
    assert "animation-duration: 0.01ms !important;" in stylesheet


def test_summary_text_protects_against_overflow() -> None:
    stylesheet = get_stylesheet()

    assert "white-space: pre-wrap;" in stylesheet
    assert "overflow-wrap: anywhere;" in stylesheet


def test_metadata_grid_has_desktop_layout() -> None:
    stylesheet = get_stylesheet()

    assert "grid-template-columns: repeat(2, minmax(0, 1fr));" in stylesheet


def test_metadata_grid_has_narrow_layout() -> None:
    stylesheet = get_stylesheet()

    assert "grid-template-columns: 1fr;" in stylesheet


def test_input_toolbar_has_narrow_layout() -> None:
    stylesheet = get_stylesheet()

    assert ".input-toolbar {" in stylesheet
    assert "flex-direction: column;" in stylesheet


def test_reflow_does_not_depend_on_fixed_page_width() -> None:
    stylesheet = get_stylesheet()

    assert "max-width:" in stylesheet
    assert "width: 100%;" in stylesheet


def test_hidden_utility_remains_available() -> None:
    stylesheet = get_stylesheet()

    assert ".hidden {" in stylesheet
    assert "display: none" in stylesheet


def test_error_region_remains_available() -> None:
    html = get_html()

    assert 'id="error"' in html


def test_empty_and_success_result_states_both_exist() -> None:
    html = get_html()

    assert html.count('id="resultEmpty"') == 1
    assert html.count('id="result"') == 1


def test_m2_remains_free_of_deferred_product_actions() -> None:
    html = get_html()

    assert 'id="copyButton"' not in html
    assert 'id="downloadButton"' not in html
    assert 'id="regenerateButton"' not in html
