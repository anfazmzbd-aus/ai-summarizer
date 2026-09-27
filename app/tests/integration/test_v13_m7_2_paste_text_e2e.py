"""V13 M7.2 paste-text end-to-end integration certification.

These tests certify the complete browser paste-text workflow across the
frozen V13 MVP boundaries.

M7.2 does not introduce product functionality. It verifies that the
frontend, public request contract, canonical summarization endpoint,
product controls, model selection, result workspace, and recovery
behavior remain connected as one coherent product workflow.

Baseline:
    v13.0.0-m6

Architecture:
    Browser
        -> POST /api/v1/summarize
        -> SummarizationApplication
        -> bounded intelligence
        -> V9 summarization pipeline
        -> configured provider runtime
        -> product-safe response
        -> result workspace
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"

AI_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "ai.py"

APPLICATION_PATH = PROJECT_ROOT / "app" / "api" / "application.py"


def read_index_html() -> str:
    return INDEX_HTML_PATH.read_text(encoding="utf-8")


def read_app_js() -> str:
    return APP_JS_PATH.read_text(encoding="utf-8")


def read_ai_route() -> str:
    return AI_ROUTE_PATH.read_text(encoding="utf-8")


def read_application() -> str:
    return APPLICATION_PATH.read_text(encoding="utf-8")


def get_submit_handler(js: str) -> str:
    start = js.index("summaryForm.addEventListener(")

    return js[start:]


def get_regenerate_function(js: str) -> str:
    start = js.index("function regenerateSummary()")

    end = js.index(
        "summaryForm.addEventListener(",
        start,
    )

    return js[start:end]


def get_set_ui_state_function(js: str) -> str:
    start = js.index("function setUIState(")

    end = js.index(
        "function setModelState(",
        start,
    )

    return js[start:end]


# ---------------------------------------------------------------------------
# Paste-text source workspace
# ---------------------------------------------------------------------------


def test_source_textarea_exists():
    html = read_index_html()

    assert 'id="inputText"' in html
    assert "<textarea" in html


def test_source_textarea_is_part_of_summary_form():
    html = read_index_html()

    form_start = html.index('id="summaryForm"')

    form_end = html.index(
        "</form>",
        form_start,
    )

    form = html[form_start:form_end]

    assert 'id="inputText"' in form


def test_source_metrics_are_present():
    html = read_index_html()

    assert 'id="wordCount"' in html
    assert 'id="characterCount"' in html


def test_input_listener_updates_source_state():
    js = read_app_js()

    assert 'inputText.addEventListener("input", updateInputState);' in js


def test_pasted_source_is_normalized_before_submission():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "inputText.value.trim()" in submit_handler


def test_empty_source_is_not_submitted():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "normalizedText" in submit_handler

    assert "if (!normalizedText)" in submit_handler


# ---------------------------------------------------------------------------
# Product controls
# ---------------------------------------------------------------------------


def test_summary_type_control_exists():
    html = read_index_html()

    assert 'id="summaryType"' in html


def test_summary_length_control_exists():
    html = read_index_html()

    assert 'id="summaryLength"' in html


def test_custom_instructions_control_exists():
    html = read_index_html()

    assert 'id="customInstructions"' in html


def test_product_model_control_exists():
    html = read_index_html()

    assert 'id="modelSelection"' in html


def test_submit_uses_current_summary_type():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "summary_type: summaryType.value" in submit_handler


def test_submit_uses_current_summary_length():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "summary_length: summaryLength.value" in submit_handler


def test_submit_uses_current_custom_instructions():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "instructions:" in submit_handler

    assert "customInstructions.value.trim()" in submit_handler


def test_submit_uses_public_product_model_selection():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "product_model: modelSelection.value" in submit_handler


# ---------------------------------------------------------------------------
# Canonical browser request
# ---------------------------------------------------------------------------


def test_browser_has_single_summarization_fetch():
    js = read_app_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_submit_handler_calls_canonical_summarization_endpoint():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert 'fetch("/api/v1/summarize"' in submit_handler


def test_submit_request_uses_post():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert 'method: "POST"' in submit_handler


def test_submit_request_uses_json():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert '"Content-Type": "application/json"' in submit_handler

    assert "JSON.stringify(" in submit_handler


def test_submit_request_contains_current_source():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "text: normalizedText" in submit_handler


def test_frontend_does_not_build_provider_prompt():
    js = read_app_js().lower()

    forbidden = (
        "system_prompt",
        "systemprompt",
        "provider_prompt",
        "providerprompt",
        "prompt_template",
        "prompttemplate",
    )

    for value in forbidden:
        assert value not in js


# ---------------------------------------------------------------------------
# Canonical server boundary
# ---------------------------------------------------------------------------


def test_summarize_route_exists():
    route = read_ai_route()

    assert "/summarize" in route


def test_ai_route_references_summarization_application():
    route = read_ai_route()

    assert "SummarizationApplication" in route


def test_canonical_application_definition_exists():
    application = read_application()

    assert "class SummarizationApplication" in application


def test_frontend_does_not_reference_pipeline_directly():
    js = read_app_js().lower()

    assert "summarizationpipeline" not in js

    assert "summarization_pipeline" not in js


def test_frontend_does_not_reference_bounded_intelligence_directly():
    js = read_app_js().lower()

    assert "bounded_intelligence" not in js

    assert "boundedintelligence" not in js


# ---------------------------------------------------------------------------
# Processing state
# ---------------------------------------------------------------------------


def test_submit_enters_loading_state():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "UI_STATE.LOADING" in submit_handler

    assert '"Generating summary..."' in submit_handler


def test_loading_state_prevents_duplicate_submission():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "currentState === UI_STATE.LOADING" in submit_handler


def test_loading_state_disables_result_actions():
    js = read_app_js()

    assert "currentState === UI_STATE.LOADING" in js

    assert "copySummaryButton.disabled" in js

    assert "downloadSummaryButton.disabled" in js

    assert "regenerateSummaryButton.disabled" in js


# ---------------------------------------------------------------------------
# Successful response integration
# ---------------------------------------------------------------------------


def test_successful_response_updates_summary_text():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "const payload = await response.json();" in submit_handler

    assert "summaryText.textContent = payload.summary;" in submit_handler


def test_successful_response_enters_success_state():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "setUIState(UI_STATE.SUCCESS);" in submit_handler


def test_successful_result_receives_focus():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "summaryContent.focus();" in submit_handler


def test_success_refreshes_result_action_eligibility():
    js = read_app_js()
    submit_handler = get_submit_handler(js)
    ui_state = get_set_ui_state_function(js)

    assert "setUIState(UI_STATE.SUCCESS);" in submit_handler

    assert "updateResultActionEligibility();" in ui_state


# ---------------------------------------------------------------------------
# Product-safe result metadata
# ---------------------------------------------------------------------------


def test_result_workspace_contains_safe_metadata_targets():
    html = read_index_html()

    safe_ids = (
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
    )

    for safe_id in safe_ids:
        assert f'id="{safe_id}"' in html


def test_processing_details_are_native_collapsible_disclosure():
    html = read_index_html()

    assert '<details class="result-details">' in html

    assert 'id="processingDetailsHeading"' in html


def test_processing_details_are_collapsed_by_default():
    html = read_index_html()

    start = html.index('<details class="result-details">')

    opening_tag_end = html.index(
        ">",
        start,
    )

    opening_tag = html[start : opening_tag_end + 1]

    assert " open" not in opening_tag


def test_frontend_does_not_expose_provider_secrets():
    html = read_index_html().lower()
    js = read_app_js().lower()

    forbidden = (
        "openai_api_key",
        "api key",
        "api_key",
        "openai_base_url",
        "authorization: bearer",
    )

    for value in forbidden:
        assert value not in html
        assert value not in js


# ---------------------------------------------------------------------------
# Result actions
# ---------------------------------------------------------------------------


def test_copy_action_uses_rendered_summary():
    js = read_app_js()

    assert "summaryText.textContent" in js

    assert "navigator.clipboard.writeText" in js


def test_download_action_uses_rendered_summary():
    js = read_app_js()

    assert "new Blob(" in js

    assert "summaryText.textContent" in js

    assert "text/plain;charset=utf-8" in js


def test_download_is_client_side_only():
    js = read_app_js()

    assert "URL.createObjectURL" in js

    assert "URL.revokeObjectURL" in js


def test_no_backend_result_export_endpoint_is_used():
    js = read_app_js().lower()

    forbidden = (
        "/api/v1/export",
        "/api/v1/download",
        "/api/v1/results/download",
    )

    for endpoint in forbidden:
        assert endpoint not in js


# ---------------------------------------------------------------------------
# Regeneration integration
# ---------------------------------------------------------------------------


def test_regenerate_reuses_summary_form():
    js = read_app_js()
    regenerate = get_regenerate_function(js)

    assert "summaryForm.requestSubmit()" in regenerate


def test_regenerate_does_not_call_fetch_directly():
    js = read_app_js()
    regenerate = get_regenerate_function(js)

    assert "fetch(" not in regenerate


def test_regenerate_has_no_alternate_api_endpoint():
    js = read_app_js().lower()

    forbidden = (
        "/api/v1/regenerate",
        "/api/v1/retry-summary",
        "/api/v1/resummarize",
    )

    for endpoint in forbidden:
        assert endpoint not in js


def test_regeneration_uses_current_source_and_controls():
    js = read_app_js()

    regenerate = get_regenerate_function(js)
    submit_handler = get_submit_handler(js)

    assert "summaryForm.requestSubmit()" in regenerate

    assert "inputText.value.trim()" in submit_handler

    assert "summaryType.value" in submit_handler

    assert "summaryLength.value" in submit_handler

    assert "modelSelection.value" in submit_handler

    assert "customInstructions.value.trim()" in submit_handler


# ---------------------------------------------------------------------------
# Failure and recovery
# ---------------------------------------------------------------------------


def test_request_failure_enters_error_state():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "catch" in submit_handler

    assert "UI_STATE.ERROR" in submit_handler


def test_error_path_does_not_clear_existing_summary():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    catch_start = submit_handler.index("catch")

    error_path = submit_handler[catch_start:]

    assert 'summaryText.textContent = ""' not in error_path


def test_loading_path_does_not_clear_existing_summary():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    loading_start = submit_handler.index("UI_STATE.LOADING")

    fetch_start = submit_handler.index(
        'fetch("/api/v1/summarize"',
        loading_start,
    )

    loading_path = submit_handler[loading_start:fetch_start]

    assert 'summaryText.textContent = ""' not in loading_path


# ---------------------------------------------------------------------------
# Paste-text path independence from file extraction
# ---------------------------------------------------------------------------


def test_paste_text_submission_does_not_require_file_extraction():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "/api/v1/files/extract" not in submit_handler


def test_file_extraction_is_not_part_of_summary_submission():
    js = read_app_js()

    submit_handler = get_submit_handler(js)

    assert 'fetch("/api/v1/summarize"' in submit_handler

    assert "/api/v1/files/extract" not in submit_handler


# ---------------------------------------------------------------------------
# Persistence boundary
# ---------------------------------------------------------------------------


def test_frontend_does_not_persist_source_or_result_locally():
    js = read_app_js().lower()

    forbidden = (
        "localstorage",
        "sessionstorage",
        "indexeddb",
    )

    for value in forbidden:
        assert value not in js


def test_frontend_has_no_history_api():
    js = read_app_js().lower()

    forbidden = (
        "/api/v1/history",
        "/api/v1/results",
        "/api/v1/summaries/history",
    )

    for endpoint in forbidden:
        assert endpoint not in js


# ---------------------------------------------------------------------------
# M7.2 architecture boundary
# ---------------------------------------------------------------------------


def test_m7_2_preserves_single_browser_summarization_path():
    js = read_app_js()

    assert js.count('fetch("/api/v1/summarize"') == 1

    regenerate = get_regenerate_function(js)

    assert "summaryForm.requestSubmit()" in regenerate

    assert "fetch(" not in regenerate


def test_m7_2_paste_workflow_reaches_canonical_application_boundary():
    js = read_app_js()
    route = read_ai_route()
    application = read_application()

    assert 'fetch("/api/v1/summarize"' in js

    assert "/summarize" in route

    assert "SummarizationApplication" in route

    assert "class SummarizationApplication" in application
