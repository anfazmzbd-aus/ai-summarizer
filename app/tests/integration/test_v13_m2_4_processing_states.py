"""V13 M2.4 frontend processing-state contract tests."""

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


def test_processing_button_exposes_loading_targets() -> None:
    html = get_frontend_html()

    assert 'id="buttonSpinner"' in html
    assert 'id="buttonLabel"' in html
    assert 'aria-hidden="true"' in html


def test_processing_status_is_accessibly_announced() -> None:
    html = get_frontend_html()

    assert 'id="status"' in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert 'aria-atomic="true"' in html


def test_javascript_defines_explicit_ui_states() -> None:
    javascript = get_frontend_javascript()

    assert "const UI_STATE = Object.freeze({" in javascript
    assert 'IDLE: "idle"' in javascript
    assert 'LOADING: "loading"' in javascript
    assert 'SUCCESS: "success"' in javascript
    assert 'ERROR: "error"' in javascript


def test_javascript_tracks_current_ui_state() -> None:
    javascript = get_frontend_javascript()

    assert "let currentState = UI_STATE.IDLE;" in javascript
    assert 'function setUIState(nextState, message = "")' in javascript
    assert "currentState = nextState;" in javascript
    assert "document.body.dataset.uiState = nextState;" in javascript


def test_loading_state_prevents_duplicate_submission() -> None:
    javascript = get_frontend_javascript()

    assert "if (currentState === UI_STATE.LOADING)" in javascript
    assert "return;" in javascript


def test_loading_state_disables_submit_button() -> None:
    javascript = get_frontend_javascript()

    assert "function updateSubmitEligibility()" in javascript
    assert "currentState === UI_STATE.LOADING" in javascript
    assert "!hasValidInput()" in javascript


def test_loading_state_changes_button_presentation() -> None:
    javascript = get_frontend_javascript()

    assert "function setLoadingButton(isLoading)" in javascript
    assert '"Summarizing..."' in javascript
    assert '"Summarize"' in javascript
    assert "buttonSpinner.classList.toggle(" in javascript


def test_request_enters_loading_state_before_fetch() -> None:
    javascript = get_frontend_javascript()

    normalized_javascript = javascript.replace("\r\n", "\n")

    loading_position = normalized_javascript.index(
        "setUIState(\n" "        UI_STATE.LOADING"
    )
    fetch_position = normalized_javascript.index('fetch("/api/v1/summarize"')

    assert loading_position < fetch_position


def test_successful_request_enters_success_state() -> None:
    javascript = get_frontend_javascript()

    assert "setUIState(UI_STATE.SUCCESS);" in javascript


def test_failed_request_enters_error_state() -> None:
    javascript = get_frontend_javascript()

    assert "setUIState(UI_STATE.ERROR, message);" in javascript


def test_error_state_preserves_safe_fallback_message() -> None:
    javascript = get_frontend_javascript()

    assert '"The summarization request failed."' in javascript
    assert "requestError instanceof Error" in javascript


def test_success_state_controls_result_visibility() -> None:
    javascript = get_frontend_javascript()

    assert "function showResult()" in javascript
    assert 'resultEmpty.classList.add("hidden");' in javascript
    assert 'result.classList.remove("hidden");' in javascript


def test_idle_state_controls_empty_result_visibility() -> None:
    javascript = get_frontend_javascript()

    assert "function showEmptyResult()" in javascript
    assert 'result.classList.add("hidden");' in javascript
    assert 'resultEmpty.classList.remove("hidden");' in javascript


def test_processing_state_preserves_canonical_api_path() -> None:
    javascript = get_frontend_javascript()

    assert 'fetch("/api/v1/summarize"' in javascript
    assert 'fetch("/summarize"' not in javascript


def test_processing_styles_define_button_spinner() -> None:
    stylesheet = get_frontend_stylesheet()

    assert ".button-spinner {" in stylesheet
    assert "@keyframes button-spin" in stylesheet
    assert "animation: button-spin 700ms linear infinite;" in stylesheet


def test_processing_styles_expose_loading_state_hook() -> None:
    stylesheet = get_frontend_stylesheet()

    assert 'body[data-ui-state="loading"] textarea' in stylesheet
    assert 'body[data-ui-state="loading"] .input-metrics' in stylesheet


def test_existing_reduced_motion_contract_remains_available() -> None:
    stylesheet = get_frontend_stylesheet()

    assert "@media (prefers-reduced-motion: reduce)" in stylesheet
    assert "animation-duration: 0.01ms !important;" in stylesheet


def test_frontend_initializes_idle_state() -> None:
    javascript = get_frontend_javascript()

    normalized_javascript = javascript.replace("\r\n", "\n")

    assert "updateInputState();" in normalized_javascript
    assert "setUIState(UI_STATE.IDLE);" in normalized_javascript

    input_state_position = normalized_javascript.rfind("updateInputState();")
    idle_state_position = normalized_javascript.rfind("setUIState(UI_STATE.IDLE);")

    assert input_state_position < idle_state_position
