from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"
INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"


def read_app_js() -> str:
    return APP_JS_PATH.read_text(encoding="utf-8")


def read_index_html() -> str:
    return INDEX_HTML_PATH.read_text(encoding="utf-8")


def test_result_actions_remain_bound_to_existing_controls():
    js = read_app_js()

    for control_id in (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ):
        assert f'"{control_id}"' in js


def test_result_action_eligibility_is_centralized():
    js = read_app_js()

    assert "function updateResultActionEligibility()" in js
    assert "copySummaryButton.disabled = actionsDisabled;" in js
    assert "downloadSummaryButton.disabled = actionsDisabled;" in js
    assert "regenerateSummaryButton.disabled =" in js


def test_copy_and_download_require_existing_successful_result():
    js = read_app_js()

    assert "function hasSummaryResult()" in js
    assert "!hasSummaryResult()" in js
    assert "summaryText.textContent.trim().length > 0" in js


def test_result_actions_are_disabled_during_active_summary_request():
    js = read_app_js()

    assert "currentState === UI_STATE.LOADING" in js
    assert "const actionsDisabled =" in js
    assert "copySummaryButton.disabled = actionsDisabled;" in js
    assert "downloadSummaryButton.disabled = actionsDisabled;" in js


def test_regenerate_remains_blocked_during_file_extraction():
    js = read_app_js()

    assert "fileExtractionInProgress" in js
    assert "actionsDisabled || fileExtractionInProgress ||" in js


def test_regenerate_requires_current_valid_source():
    js = read_app_js()

    assert "function hasValidInput()" in js
    assert "!hasValidInput()" in js
    assert "inputText.value.trim().length > 0" in js


def test_regenerate_requires_current_available_model():
    js = read_app_js()

    assert "function hasAvailableModel()" in js
    assert "!hasAvailableModel()" in js
    assert "currentModelState === MODEL_STATE.READY" in js


def test_input_changes_refresh_result_action_eligibility():
    js = read_app_js()

    assert "function updateInputState()" in js
    assert "updateResultActionEligibility();" in js
    assert 'inputText.addEventListener("input", updateInputState);' in js


def test_model_changes_refresh_result_action_eligibility():
    js = read_app_js()

    assert "modelSelection.addEventListener(" in js
    assert '"change"' in js
    assert "updateSubmitEligibility();" in js
    assert "updateResultActionEligibility();" in js


def test_file_extraction_state_refreshes_result_action_eligibility():
    js = read_app_js()

    assert "function setFileExtractionState(isLoading)" in js
    assert "fileExtractionInProgress = isLoading;" in js
    assert "updateResultActionEligibility();" in js


def test_regenerate_reuses_existing_form_submission_path():
    js = read_app_js()

    assert "function regenerateSummary()" in js
    assert "summaryForm.requestSubmit();" in js
    assert "summaryForm.addEventListener(\n" '    "submit",' in js


def test_regenerate_does_not_create_alternate_summary_endpoint():
    js = read_app_js()

    assert js.count('fetch("/api/v1/summarize"') == 1
    assert "/api/v1/regenerate" not in js
    assert "/api/v1/resummarize" not in js


def test_loading_transition_clears_stale_copy_feedback():
    js = read_app_js()

    loading_start = js.index("if (nextState === UI_STATE.LOADING) {")
    loading_end = js.index(
        "if (nextState === UI_STATE.SUCCESS) {",
        loading_start,
    )
    loading_block = js[loading_start:loading_end]

    assert 'setCopySummaryStatus("");' in loading_block


def test_successful_result_clears_previous_copy_feedback():
    js = read_app_js()

    assert 'setCopySummaryStatus("");' in js

    success_assignment = js.index("summaryText.textContent = payload.summary;")
    clear_status = js.index(
        'setCopySummaryStatus("");',
        success_assignment,
    )
    success_state = js.index(
        "setUIState(UI_STATE.SUCCESS);",
        success_assignment,
    )

    assert success_assignment < clear_status < success_state


def test_failed_regeneration_preserves_existing_summary():
    js = read_app_js()

    error_start = js.index("if (nextState === UI_STATE.ERROR) {")
    error_end = js.index(
        "updateSubmitEligibility();",
        error_start,
    )
    error_block = js[error_start:error_end]

    assert "summaryText.textContent =" not in error_block
    assert "showEmptyResult();" not in error_block


def test_loading_state_preserves_existing_summary():
    js = read_app_js()

    loading_start = js.index("if (nextState === UI_STATE.LOADING) {")
    loading_end = js.index(
        "if (nextState === UI_STATE.SUCCESS) {",
        loading_start,
    )
    loading_block = js[loading_start:loading_end]

    assert "summaryText.textContent =" not in loading_block
    assert "showEmptyResult();" not in loading_block


def test_new_successful_result_replaces_previous_summary():
    js = read_app_js()

    assert "summaryText.textContent = payload.summary;" in js
    assert js.count("summaryText.textContent = payload.summary;") == 1


def test_successful_result_restores_result_workspace():
    js = read_app_js()

    success_start = js.index("if (nextState === UI_STATE.SUCCESS) {")
    success_end = js.index(
        "if (nextState === UI_STATE.ERROR) {",
        success_start,
    )
    success_block = js[success_start:success_end]

    assert "showResult();" in success_block


def test_successful_result_moves_focus_to_summary():
    js = read_app_js()

    assert "setUIState(UI_STATE.SUCCESS);" in js
    assert "summaryContent.focus();" in js

    success_state = js.index("setUIState(UI_STATE.SUCCESS);")
    result_focus = js.index(
        "summaryContent.focus();",
        success_state,
    )

    assert success_state < result_focus


def test_file_extraction_does_not_submit_summary():
    js = read_app_js()

    extraction_start = js.index("async function extractFile(file)")
    extraction_end = js.index(
        "function handleSelectedFiles(files)",
        extraction_start,
    )
    extraction_block = js[extraction_start:extraction_end]

    assert "summaryForm.requestSubmit()" not in extraction_block
    assert "/api/v1/summarize" not in extraction_block


def test_copy_operates_only_on_rendered_summary_text():
    js = read_app_js()

    assert (
        "navigator.clipboard.writeText(\n" "            summaryText.textContent" in js
    )


def test_download_operates_only_on_rendered_summary_text():
    js = read_app_js()

    assert "const summary = summaryText.textContent;" in js
    assert "new Blob(" in js
    assert '{ type: "text/plain;charset=utf-8" }' in js


def test_processing_details_remain_collapsed_by_default():
    html = read_index_html()

    assert '<details class="result-details">' in html
    assert '<details class="result-details" open>' not in html


def test_result_details_remain_product_safe():
    html = read_index_html()

    for metadata_id in (
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
    ):
        assert f'id="{metadata_id}"' in html

    forbidden_terms = (
        "api key",
        "api_key",
        "base url",
        "base_url",
        "environment variable",
        "stack trace",
        "system prompt",
        "provider prompt",
    )

    normalized_html = html.lower()

    for forbidden_term in forbidden_terms:
        assert forbidden_term not in normalized_html


def test_m6_6_introduces_no_browser_provider_runtime_logic():
    js = read_app_js()

    forbidden_terms = (
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "AsyncOpenAI",
        "OpenAIProvider",
        "SummarizationApplication(",
    )

    for forbidden_term in forbidden_terms:
        assert forbidden_term not in js
