from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"
APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"


def read_index_html() -> str:
    return INDEX_HTML_PATH.read_text(encoding="utf-8")


def read_app_js() -> str:
    return APP_JS_PATH.read_text(encoding="utf-8")


def get_submit_handler(js: str) -> str:
    start = js.index("summaryForm.addEventListener(\n" '    "submit",')

    return js[start:]


def get_regenerate_function(js: str) -> str:
    start = js.index("function regenerateSummary()")

    end = js.index(
        "regenerateSummaryButton.addEventListener(",
        start,
    )

    return js[start:end]


def get_copy_function(js: str) -> str:
    start = js.index("async function copySummary()")

    end = js.index(
        "copySummaryButton.addEventListener(",
        start,
    )

    return js[start:end]


def get_download_function(js: str) -> str:
    start = js.index("function downloadSummary()")

    end = js.index(
        "downloadSummaryButton.addEventListener(",
        start,
    )

    return js[start:end]


def get_extraction_function(js: str) -> str:
    start = js.index("async function extractFile(file)")

    end = js.index(
        "function handleSelectedFiles(files)",
        start,
    )

    return js[start:end]


def test_result_workspace_contains_all_mvp_actions():
    html = read_index_html()

    for control_id in (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ):
        assert f'id="{control_id}"' in html


def test_result_actions_are_non_submit_controls():
    html = read_index_html()

    for control_id in (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ):
        control_start = html.index(f'id="{control_id}"')

        surrounding_markup = html[max(0, control_start - 150) : control_start + 250]

        assert 'type="button"' in surrounding_markup


def test_result_workspace_contains_rendered_summary_target():
    html = read_index_html()

    assert 'id="summaryContent"' in html
    assert 'id="summaryText"' in html


def test_copy_status_remains_accessible():
    html = read_index_html()

    assert 'id="copySummaryStatus"' in html

    status_start = html.index('id="copySummaryStatus"')

    surrounding_markup = html[max(0, status_start - 200) : status_start + 300]

    assert (
        'aria-live="polite"' in surrounding_markup
        or 'role="status"' in surrounding_markup
    )


def test_copy_uses_rendered_summary_only():
    js = read_app_js()
    copy_function = get_copy_function(js)

    assert "summaryText.textContent" in copy_function
    assert "navigator.clipboard.writeText(" in copy_function

    assert "inputText.value" not in copy_function
    assert "metadata" not in copy_function
    assert "product_model" not in copy_function
    assert "instructions" not in copy_function


def test_download_uses_rendered_summary_only():
    js = read_app_js()
    download_function = get_download_function(js)

    assert "const summary = summaryText.textContent;" in download_function

    assert "new Blob(" in download_function
    assert '{ type: "text/plain;charset=utf-8" }' in download_function

    assert "inputText.value" not in download_function
    assert "metadata" not in download_function
    assert "product_model" not in download_function


def test_download_remains_entirely_client_side():
    js = read_app_js()
    download_function = get_download_function(js)

    assert "fetch(" not in download_function
    assert "XMLHttpRequest" not in download_function
    assert "/api/" not in download_function

    assert "URL.createObjectURL(" in download_function
    assert "URL.revokeObjectURL(" in download_function


def test_download_filename_uses_ai_summary_txt_contract():
    js = read_app_js()

    assert "function buildSummaryDownloadFileName(" in js

    assert "ai-summary-" in js
    assert ".txt" in js


def test_regenerate_reuses_existing_form_submission():
    js = read_app_js()
    regenerate_function = get_regenerate_function(js)

    assert "summaryForm.requestSubmit();" in regenerate_function

    assert "fetch(" not in regenerate_function
    assert "/api/" not in regenerate_function


def test_browser_has_only_one_summarization_fetch():
    js = read_app_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_canonical_summary_endpoint_remains_unchanged():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert 'fetch("/api/v1/summarize", {' in submit_handler

    assert 'method: "POST"' in submit_handler


def test_submit_handler_uses_current_source_text():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "const normalizedText = " "inputText.value.trim();" in submit_handler

    assert "text: normalizedText" in submit_handler


def test_submit_handler_uses_current_product_model():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "product_model: modelSelection.value" in submit_handler


def test_submit_handler_uses_current_summary_type():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "summary_type: summaryType.value" in submit_handler


def test_submit_handler_uses_current_summary_length():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "summary_length: summaryLength.value" in submit_handler


def test_submit_handler_uses_current_custom_instructions():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "instructions: " "customInstructions.value.trim() || null" in submit_handler


def test_result_actions_require_existing_summary():
    js = read_app_js()

    assert "function hasSummaryResult()" in js

    assert "summaryText.textContent.trim().length > 0" in js

    assert "!hasSummaryResult()" in js


def test_result_actions_are_locked_during_loading():
    js = read_app_js()

    assert "currentState === UI_STATE.LOADING" in js

    assert "copySummaryButton.disabled = actionsDisabled;" in js

    assert "downloadSummaryButton.disabled = actionsDisabled;" in js


def test_regenerate_is_locked_during_file_extraction():
    js = read_app_js()
    regenerate_function = get_regenerate_function(js)

    assert "fileExtractionInProgress" in regenerate_function


def test_regenerate_requires_current_valid_input():
    js = read_app_js()
    regenerate_function = get_regenerate_function(js)

    assert "!hasValidInput()" in regenerate_function


def test_regenerate_requires_current_available_model():
    js = read_app_js()
    regenerate_function = get_regenerate_function(js)

    assert "!hasAvailableModel()" in regenerate_function


def test_loading_preserves_existing_result():
    js = read_app_js()

    start = js.index("if (nextState === UI_STATE.LOADING) {")

    end = js.index(
        "if (nextState === UI_STATE.SUCCESS) {",
        start,
    )

    loading_block = js[start:end]

    assert "summaryText.textContent =" not in loading_block
    assert "showEmptyResult();" not in loading_block


def test_error_preserves_existing_result():
    js = read_app_js()

    start = js.index("if (nextState === UI_STATE.ERROR) {")

    end = js.index(
        "updateSubmitEligibility();",
        start,
    )

    error_block = js[start:end]

    assert "summaryText.textContent =" not in error_block
    assert "showEmptyResult();" not in error_block


def test_new_success_replaces_previous_summary():
    js = read_app_js()

    assert js.count("summaryText.textContent = payload.summary;") == 1


def test_new_success_refreshes_product_safe_metadata():
    js = read_app_js()

    expected_assignments = (
        "strategyValue.textContent =",
        "chunkCountValue.textContent =",
        "intelligenceModeValue.textContent =",
        "observabilityStatusValue.textContent =",
    )

    for assignment in expected_assignments:
        assert assignment in js


def test_successful_summary_moves_focus_to_result():
    js = read_app_js()

    success_position = js.index("setUIState(UI_STATE.SUCCESS);")

    focus_position = js.index(
        "summaryContent.focus();",
        success_position,
    )

    assert success_position < focus_position


def test_copy_feedback_is_cleared_for_new_request():
    js = read_app_js()

    loading_start = js.index("if (nextState === UI_STATE.LOADING) {")

    loading_end = js.index(
        "if (nextState === UI_STATE.SUCCESS) {",
        loading_start,
    )

    loading_block = js[loading_start:loading_end]

    assert 'setCopySummaryStatus("");' in loading_block


def test_processing_details_are_collapsed_by_default():
    html = read_index_html()

    assert '<details class="result-details">' in html

    assert '<details class="result-details" open>' not in html


def test_processing_details_use_native_disclosure():
    html = read_index_html()

    assert "<details" in html
    assert "<summary" in html
    assert "Processing details" in html


def test_processing_details_preserve_safe_metadata_ids():
    html = read_index_html()

    for metadata_id in (
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
    ):
        assert f'id="{metadata_id}"' in html


def test_result_workspace_exposes_no_provider_secrets():
    combined = read_index_html() + "\n" + read_app_js()

    forbidden = (
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENROUTER_API_KEY",
        "api_key",
        "system_prompt",
        "provider_prompt",
    )

    for term in forbidden:
        assert term not in combined


def test_frontend_does_not_construct_provider_runtime():
    js = read_app_js()

    forbidden = (
        "AsyncOpenAI",
        "OpenAIProvider",
        "SummarizationApplication(",
        "SummarizationPipeline(",
    )

    for term in forbidden:
        assert term not in js


def test_file_extraction_endpoint_remains_separate():
    js = read_app_js()
    extraction_function = get_extraction_function(js)

    assert '"/api/v1/files/extract"' in extraction_function

    assert extraction_function.count('"/api/v1/files/extract"') == 1

    assert '"/api/v1/summarize"' in js

    assert js.count('fetch("/api/v1/summarize"') == 1

    assert "/api/v1/summarize" not in extraction_function


def test_file_extraction_does_not_auto_summarize():
    js = read_app_js()
    extraction_function = get_extraction_function(js)

    assert '"/api/v1/files/extract"' in extraction_function

    assert "fetch(" in extraction_function
    assert "/api/v1/summarize" not in extraction_function
    assert "summaryForm.requestSubmit()" not in extraction_function


def test_m6_introduces_no_history_or_persistence_api():
    js = read_app_js()

    forbidden_endpoints = (
        "/api/v1/history",
        "/api/v1/results",
        "/api/v1/export",
        "/api/v1/download",
        "/api/v1/regenerate",
        "/api/v1/resummarize",
    )

    for endpoint in forbidden_endpoints:
        assert endpoint not in js


def test_m6_result_actions_do_not_require_new_backend_endpoint():
    js = read_app_js()

    copy_function = get_copy_function(js)
    download_function = get_download_function(js)
    regenerate_function = get_regenerate_function(js)

    assert "fetch(" not in copy_function
    assert "fetch(" not in download_function
    assert "fetch(" not in regenerate_function


def test_result_workspace_preserves_mvp_action_boundaries():
    html = read_index_html()
    js = read_app_js()

    assert 'id="copySummaryButton"' in html
    assert 'id="downloadSummaryButton"' in html
    assert 'id="regenerateSummaryButton"' in html

    assert "copySummary" in js
    assert "downloadSummary" in js
    assert "regenerateSummary" in js
