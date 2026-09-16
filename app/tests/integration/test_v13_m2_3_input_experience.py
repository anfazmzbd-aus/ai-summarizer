"""V13 M2.3 frontend input-experience contract tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def get_frontend_html() -> str:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    return response.text


def get_frontend_javascript() -> str:
    response = TestClient(app).get("/static/app.js")

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def get_frontend_stylesheet() -> str:
    response = TestClient(app).get("/static/style.css")

    assert response.status_code == 200

    return response.text


def test_input_workspace_exposes_word_count() -> None:
    html = get_frontend_html()

    assert 'id="wordCount"' in html
    assert 'id="wordCountLabel"' in html
    assert ">0</strong>" in html
    assert ">words</span>" in html


def test_input_workspace_exposes_character_count() -> None:
    html = get_frontend_html()

    assert 'id="characterCount"' in html
    assert 'id="characterCountLabel"' in html
    assert ">characters</span>" in html


def test_input_metrics_are_accessibly_announced() -> None:
    html = get_frontend_html()

    assert 'id="inputMetrics"' in html
    assert 'aria-live="polite"' in html
    assert 'aria-atomic="true"' in html


def test_empty_input_starts_with_disabled_submit() -> None:
    html = get_frontend_html()

    assert 'id="summarizeButton"' in html
    assert "disabled" in html


def test_javascript_defines_word_counting_behavior() -> None:
    javascript = get_frontend_javascript()

    assert "function countWords(value)" in javascript
    assert "value.trim()" in javascript
    assert r"split(/\s+/u)" in javascript


def test_javascript_updates_input_metrics() -> None:
    javascript = get_frontend_javascript()

    assert "function updateInputState()" in javascript
    assert "wordCount.textContent = String(words);" in javascript
    assert "characterCount.textContent = String(characters);" in javascript
    assert 'inputText.addEventListener("input", updateInputState);' in javascript


def test_javascript_handles_singular_and_plural_metric_labels() -> None:
    javascript = get_frontend_javascript()

    assert "function updateMetricLabel(" in javascript
    assert '"word"' in javascript
    assert '"words"' in javascript
    assert '"character"' in javascript
    assert '"characters"' in javascript


def test_javascript_disables_submit_for_whitespace_only_input() -> None:
    javascript = get_frontend_javascript()

    assert "function hasValidInput()" in javascript
    assert "inputText.value.trim().length > 0" in javascript
    assert "function updateSubmitEligibility()" in javascript
    assert "!hasValidInput()" in javascript


def test_submit_guard_rejects_effectively_empty_input() -> None:
    javascript = get_frontend_javascript()

    assert "const normalizedText = inputText.value.trim();" in javascript
    assert "if (!normalizedText)" in javascript
    assert "inputText.focus();" in javascript


def test_canonical_request_uses_normalized_source_text() -> None:
    javascript = get_frontend_javascript()

    assert 'fetch("/api/v1/summarize"' in javascript
    assert "text: normalizedText" in javascript
    assert 'provider: "fake"' in javascript
    assert 'model: "demo"' in javascript


def test_input_toolbar_uses_design_system_tokens() -> None:
    stylesheet = get_frontend_stylesheet()

    assert ".input-toolbar {" in stylesheet
    assert ".input-metrics {" in stylesheet
    assert ".metric-separator {" in stylesheet
    assert "var(--color-text-muted)" in stylesheet
    assert "var(--font-size-xs)" in stylesheet


def test_input_toolbar_has_mobile_layout() -> None:
    stylesheet = get_frontend_stylesheet()

    assert "@media (max-width: 520px)" in stylesheet
    assert "flex-direction: column;" in stylesheet
    assert ".primary-button {" in stylesheet
    assert "width: 100%;" in stylesheet


def test_m2_3_preserves_result_workspace_behavior() -> None:
    javascript = get_frontend_javascript()

    assert 'resultEmpty.classList.add("hidden");' in javascript
    assert 'result.classList.remove("hidden");' in javascript


def test_m2_3_initializes_input_state_on_page_load() -> None:
    javascript = get_frontend_javascript()

    assert "updateInputState();" in javascript
