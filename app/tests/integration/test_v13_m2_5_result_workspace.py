"""V13 M2.5 result-workspace contract tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def get_frontend_html() -> str:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def get_frontend_javascript() -> str:
    response = TestClient(app).get("/static/app.js")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def get_frontend_stylesheet() -> str:
    response = TestClient(app).get("/static/style.css")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def test_result_workspace_has_semantic_heading() -> None:
    html = get_frontend_html()

    assert 'id="result"' in html
    assert 'class="result-workspace hidden"' in html
    assert 'aria-labelledby="resultHeading"' in html
    assert 'id="resultHeading"' in html
    assert ">Summary<" in html.replace("\n", "").replace(" ", "")


def test_result_exposes_ready_status() -> None:
    html = get_frontend_html()

    assert 'id="resultStatus"' in html
    assert 'class="result-status"' in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert "Ready" in html


def test_result_status_has_non_text_indicator() -> None:
    html = get_frontend_html()

    assert 'class="result-status-indicator"' in html
    assert 'aria-hidden="true"' in html


def test_summary_content_is_keyboard_focusable() -> None:
    html = get_frontend_html()

    assert 'id="summaryContent"' in html
    assert 'class="summary-content"' in html
    assert 'tabindex="0"' in html


def test_summary_text_target_is_preserved() -> None:
    html = get_frontend_html()

    assert html.count('id="summaryText"') == 1


def test_processing_details_are_semantically_grouped() -> None:
    html = get_frontend_html()

    assert 'class="processing-details"' in html
    assert 'aria-labelledby="processingDetailsHeading"' in html
    assert 'id="processingDetailsHeading"' in html
    assert "Processing details" in html


def test_processing_metadata_uses_description_list() -> None:
    html = get_frontend_html()

    assert '<dl class="metadata-grid">' in html
    assert "<dt>Strategy</dt>" in html
    assert "<dt>Chunks</dt>" in html
    assert "<dt>Intelligence</dt>" in html
    assert "<dt>Observability</dt>" in html


def test_metadata_targets_remain_unique() -> None:
    html = get_frontend_html()

    assert html.count('id="strategyValue"') == 1
    assert html.count('id="chunkCountValue"') == 1
    assert html.count('id="intelligenceModeValue"') == 1
    assert html.count('id="observabilityStatusValue"') == 1


def test_javascript_references_summary_content() -> None:
    javascript = get_frontend_javascript()

    assert (
        "const summaryContent = "
        'document.getElementById("summaryContent");' in javascript
    )


def test_success_moves_focus_to_result() -> None:
    javascript = get_frontend_javascript()

    success_position = javascript.index("setUIState(UI_STATE.SUCCESS);")

    focus_position = javascript.index("summaryContent.focus();")

    assert success_position < focus_position


def test_result_focus_occurs_after_summary_assignment() -> None:
    javascript = get_frontend_javascript()

    summary_position = javascript.index("summaryText.textContent = payload.summary;")

    focus_position = javascript.index("summaryContent.focus();")

    assert summary_position < focus_position


def test_result_workspace_styles_exist() -> None:
    stylesheet = get_frontend_stylesheet()

    assert ".result-workspace {" in stylesheet
    assert ".result-header {" in stylesheet
    assert ".summary-content {" in stylesheet
    assert ".processing-details {" in stylesheet
    assert ".metadata-grid {" in stylesheet


def test_summary_preserves_generated_line_breaks() -> None:
    stylesheet = get_frontend_stylesheet()

    assert "white-space: pre-wrap;" in stylesheet
    assert "overflow-wrap: anywhere;" in stylesheet


def test_summary_has_visible_keyboard_focus_contract() -> None:
    stylesheet = get_frontend_stylesheet()

    assert ".summary-content:focus-visible {" in stylesheet
    assert "outline:" in stylesheet


def test_metadata_grid_has_responsive_contract() -> None:
    stylesheet = get_frontend_stylesheet()

    assert "grid-template-columns: repeat(2, minmax(0, 1fr));" in stylesheet

    assert "grid-template-columns: 1fr;" in stylesheet


def test_m2_5_does_not_introduce_product_actions() -> None:
    html = get_frontend_html()

    assert 'id="copyButton"' not in html
    assert 'id="downloadButton"' not in html
    assert 'id="regenerateButton"' not in html
