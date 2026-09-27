"""V13 M7.3 TXT/PDF end-to-end integration certification.

This suite certifies the frozen V13 document-ingestion workflow from
browser file selection through extraction and back into the canonical
summarization workflow.

M7.3 introduces no new product functionality.

Certified architecture:

    TXT / PDF
        -> browser validation
        -> POST /api/v1/files/extract
        -> FileExtractionService
        -> normalized text
        -> source textarea
        -> existing product controls
        -> POST /api/v1/summarize
        -> SummarizationApplication
        -> existing summarization runtime
        -> result workspace

Critical invariant:

    File extraction is preprocessing only. It must never become a
    second summarization path.
"""

from pathlib import Path

from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"

FILE_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "file_extraction.py"

FILE_EXTRACTION_PATH = PROJECT_ROOT / "app" / "core" / "file_extraction.py"

AI_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "ai.py"

APPLICATION_PATH = PROJECT_ROOT / "app" / "api" / "application.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_index_html() -> str:
    return read(INDEX_HTML_PATH)


def read_app_js() -> str:
    return read(APP_JS_PATH)


def read_file_route() -> str:
    return read(FILE_ROUTE_PATH)


def read_file_extraction() -> str:
    return read(FILE_EXTRACTION_PATH)


def read_ai_route() -> str:
    return read(AI_ROUTE_PATH)


def read_application() -> str:
    return read(APPLICATION_PATH)


def get_extract_file_function(js: str) -> str:
    start = js.index("async function extractFile(")

    end = js.index(
        "function handleSelectedFiles(",
        start,
    )

    return js[start:end]


def get_handle_selected_files_function(
    js: str,
) -> str:
    start = js.index("function handleSelectedFiles(")

    end = js.index(
        "fileInput.addEventListener(",
        start,
    )

    return js[start:end]


def get_submit_handler(js: str) -> str:
    start = js.index("summaryForm.addEventListener(")

    return js[start:]


def get_extraction_error_handler(
    extraction: str,
) -> str:
    start = extraction.index("catch (extractionError)")

    end = extraction.index(
        "finally",
        start,
    )

    return extraction[start:end]


# ---------------------------------------------------------------------------
# File workspace contract
# ---------------------------------------------------------------------------


def test_file_input_exists():
    html = read_index_html()

    assert 'id="fileInput"' in html
    assert 'type="file"' in html


def test_file_input_accepts_txt_and_pdf():
    html = read_index_html()

    assert 'accept=".txt,.pdf,text/plain,application/pdf"' in html


def test_choose_file_control_exists():
    html = read_index_html()

    assert 'id="chooseFileButton"' in html


def test_drag_drop_zone_exists():
    html = read_index_html()

    assert 'id="fileDropZone"' in html


def test_drag_drop_zone_is_keyboard_accessible():
    html = read_index_html()

    assert 'tabindex="0"' in html
    assert 'role="button"' in html


def test_file_status_region_exists():
    html = read_index_html()

    assert 'id="fileStatus"' in html
    assert 'aria-live="polite"' in html


def test_file_error_region_exists():
    html = read_index_html()

    assert 'id="fileError"' in html
    assert 'role="alert"' in html


def test_clear_file_control_exists():
    html = read_index_html()

    assert 'id="clearFileButton"' in html


# ---------------------------------------------------------------------------
# Browser file validation
# ---------------------------------------------------------------------------


def test_frontend_supports_only_txt_and_pdf():
    js = read_app_js()

    assert 'Object.freeze([".txt", ".pdf"])' in js


def test_frontend_rejects_unsupported_file_type():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "if (!isSupportedFile(file))" in extraction

    assert "Choose a TXT or PDF file." in extraction


def test_frontend_has_ten_mib_upload_limit():
    js = read_app_js()

    assert "10 * 1024 * 1024" in js


def test_frontend_rejects_oversized_file_before_upload():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "file.size > MAX_FILE_SIZE_BYTES" in extraction

    assert "The uploaded file exceeds the maximum allowed size." in extraction


def test_multiple_files_are_rejected():
    js = read_app_js()
    handler = get_handle_selected_files_function(js)

    assert "files.length > 1" in handler

    assert "Upload one document at a time." in handler


def test_empty_file_selection_is_ignored():
    js = read_app_js()
    handler = get_handle_selected_files_function(js)

    assert "files.length === 0" in handler


# ---------------------------------------------------------------------------
# File picker and drag/drop integration
# ---------------------------------------------------------------------------


def test_file_picker_calls_file_processing_path():
    js = read_app_js()

    assert "fileInput.addEventListener(" in js

    assert "handleSelectedFiles(" in js


def test_drag_drop_events_are_registered():
    js = read_app_js()

    assert '"dragenter"' in js
    assert '"dragover"' in js
    assert '"dragleave"' in js
    assert '"drop"' in js


def test_drop_uses_data_transfer_files():
    js = read_app_js()

    assert "event.dataTransfer?.files" in js


def test_keyboard_file_picker_supports_enter():
    js = read_app_js()

    assert 'event.key === "Enter"' in js


def test_keyboard_file_picker_supports_space():
    js = read_app_js()

    assert 'event.key === " "' in js


def test_keyboard_file_picker_opens_file_input():
    js = read_app_js()

    assert "fileInput.click();" in js


# ---------------------------------------------------------------------------
# Extraction request boundary
# ---------------------------------------------------------------------------


def test_file_extraction_uses_public_endpoint():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert '"/api/v1/files/extract"' in extraction


def test_extraction_request_uses_post():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert 'method: "POST"' in extraction


def test_extraction_request_uses_form_data():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "new FormData()" in extraction

    assert 'formData.append("file", file)' in extraction


def test_extraction_does_not_manually_set_multipart_content_type():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert '"Content-Type"' not in extraction


def test_extraction_has_separate_loading_state():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "setFileExtractionState(true);" in extraction

    assert "setFileExtractionState(false);" in extraction


def test_extraction_state_is_released_in_finally():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "finally" in extraction

    finally_start = extraction.index("finally")

    finally_source = extraction[finally_start:]

    assert "setFileExtractionState(false);" in finally_source


# ---------------------------------------------------------------------------
# Extraction response -> source workspace
# ---------------------------------------------------------------------------


def test_extraction_validates_public_text():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert 'typeof payload.text !== "string"' in extraction

    assert "payload.text.trim().length === 0" in extraction


def test_extraction_validates_public_file_metadata():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "payload.file === null" in extraction

    assert 'typeof payload.file !== "object"' in extraction

    assert 'typeof payload.file.name !== "string"' in extraction

    assert 'typeof payload.file.type !== "string"' in extraction

    assert 'typeof payload.file.size_bytes !== "number"' in extraction


def test_successful_extraction_replaces_source_text():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "inputText.value = payload.text;" in extraction


def test_successful_extraction_updates_source_metrics():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    source_assignment = extraction.index("inputText.value = payload.text;")

    update = extraction.index(
        "updateInputState();",
        source_assignment,
    )

    assert update > source_assignment


def test_successful_extraction_focuses_source_workspace():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "inputText.focus();" in extraction


def test_successful_extraction_records_public_file_name():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "currentFileName = payload.file.name;" in extraction


def test_successful_extraction_displays_public_metadata():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "buildFileStatusMessage(payload.file)" in extraction


def test_pdf_page_count_can_be_presented():
    js = read_app_js()

    assert 'fileMetadata.type === "pdf"' in js

    assert "fileMetadata.page_count" in js


# ---------------------------------------------------------------------------
# No automatic summarization
# ---------------------------------------------------------------------------


def test_extraction_function_does_not_call_summarize_endpoint():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "/api/v1/summarize" not in extraction


def test_extraction_function_does_not_submit_summary_form():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "summaryForm.requestSubmit()" not in extraction

    assert "summaryForm.submit()" not in extraction


def test_extraction_does_not_build_summary_request():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    forbidden = (
        "summary_type",
        "summary_length",
        "product_model",
        "instructions:",
    )

    for value in forbidden:
        assert value not in extraction


def test_browser_has_exactly_one_summarization_fetch():
    js = read_app_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_browser_has_exactly_one_extraction_endpoint_reference():
    js = read_app_js()

    assert js.count('"/api/v1/files/extract"') == 1


# ---------------------------------------------------------------------------
# Extracted text -> canonical summarization
# ---------------------------------------------------------------------------


def test_summary_submission_reads_source_textarea():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "inputText.value.trim()" in submit_handler


def test_summary_submission_uses_normalized_source():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "text: normalizedText" in submit_handler


def test_extracted_source_uses_same_summary_endpoint_as_pasted_text():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert 'fetch("/api/v1/summarize"' in submit_handler


def test_extracted_source_preserves_summary_type_control():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "summary_type: summaryType.value" in submit_handler


def test_extracted_source_preserves_summary_length_control():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "summary_length: summaryLength.value" in submit_handler


def test_extracted_source_preserves_custom_instructions():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "customInstructions.value.trim()" in submit_handler


def test_extracted_source_preserves_product_model_selection():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "product_model: modelSelection.value" in submit_handler


# ---------------------------------------------------------------------------
# Extraction/summarization concurrency boundary
# ---------------------------------------------------------------------------


def test_file_extraction_state_is_tracked():
    js = read_app_js()

    assert "let fileExtractionInProgress = false;" in js


def test_summary_submit_eligibility_considers_file_extraction():
    js = read_app_js()

    assert "fileExtractionInProgress ||" in js


def test_file_selection_is_blocked_while_extraction_runs():
    js = read_app_js()
    handler = get_handle_selected_files_function(js)

    assert "fileExtractionInProgress ||" in handler


def test_regeneration_is_blocked_during_file_extraction():
    js = read_app_js()

    regenerate_start = js.index("function regenerateSummary()")

    regenerate_end = js.index(
        "regenerateSummaryButton.addEventListener(",
        regenerate_start,
    )

    regenerate = js[regenerate_start:regenerate_end]

    assert "fileExtractionInProgress ||" in regenerate


# ---------------------------------------------------------------------------
# File failure and recovery
# ---------------------------------------------------------------------------


def test_failed_extraction_uses_safe_server_detail():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert 'typeof payload.detail === "string"' in extraction

    assert "The document could not be processed." in extraction


def test_invalid_extraction_response_has_safe_error():
    js = read_app_js()
    extraction = get_extract_file_function(js)

    assert "The document extraction response is invalid." in extraction


def test_failed_extraction_clears_file_status():
    js = read_app_js()
    extraction = get_extract_file_function(js)
    error_handler = get_extraction_error_handler(extraction)

    assert "clearFileStatus();" in error_handler


def test_failed_extraction_does_not_clear_source_text():
    js = read_app_js()
    extraction = get_extract_file_function(js)
    error_handler = get_extraction_error_handler(extraction)

    assert "inputText.value" not in error_handler


def test_clear_file_status_does_not_clear_source_text():
    js = read_app_js()

    start = js.index("function clearFileStatus()")

    end = js.index(
        "function resetFileSelection()",
        start,
    )

    clear_status = js[start:end]

    assert "inputText.value" not in clear_status


def test_reset_file_selection_does_not_clear_source_text():
    js = read_app_js()

    start = js.index("function resetFileSelection()")

    end = js.index(
        "function formatFileSize(",
        start,
    )

    reset = js[start:end]

    assert "inputText.value" not in reset


# ---------------------------------------------------------------------------
# Server extraction boundary
# ---------------------------------------------------------------------------


def test_extraction_route_exists():
    paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/files/extract" in paths


def test_extraction_route_uses_file_extraction_service():
    route = read_file_route()

    assert "FileExtractionService" in route


def test_file_extraction_service_exists():
    source = read_file_extraction()

    assert "class FileExtractionService" in source


def test_server_file_extraction_supports_txt():
    source = read_file_extraction().lower()

    assert "txt" in source


def test_server_file_extraction_supports_pdf():
    source = read_file_extraction().lower()

    assert "pdf" in source


def test_server_file_extraction_does_not_reference_summarization_application():
    source = read_file_route() + "\n" + read_file_extraction()

    assert "SummarizationApplication" not in source


def test_server_file_extraction_does_not_reference_summarization_pipeline():
    source = (read_file_route() + "\n" + read_file_extraction()).lower()

    assert "summarization_pipeline" not in source

    assert "summarizationpipeline" not in source


def test_server_file_extraction_does_not_reference_provider_runtime():
    source = (read_file_route() + "\n" + read_file_extraction()).lower()

    forbidden = (
        "openai_api_key",
        "openai_base_url",
        "llmprovider",
        "llm_provider",
    )

    for value in forbidden:
        assert value not in source


# ---------------------------------------------------------------------------
# Canonical summarization boundary remains intact
# ---------------------------------------------------------------------------


def test_ai_route_still_references_summarization_application():
    route = read_ai_route()

    assert "SummarizationApplication" in route


def test_canonical_summarization_application_still_exists():
    application = read_application()

    assert "class SummarizationApplication" in application


def test_file_extraction_does_not_replace_summarization_route():
    js = read_app_js()

    assert '"/api/v1/files/extract"' in js

    assert 'fetch("/api/v1/summarize"' in js


# ---------------------------------------------------------------------------
# Persistence and security boundaries
# ---------------------------------------------------------------------------


def test_frontend_does_not_persist_uploaded_document():
    js = read_app_js().lower()

    forbidden = (
        "localstorage",
        "sessionstorage",
        "indexeddb",
    )

    for value in forbidden:
        assert value not in js


def test_frontend_does_not_send_provider_secrets_during_extraction():
    extraction = get_extract_file_function(read_app_js()).lower()

    forbidden = (
        "api_key",
        "openai_api_key",
        "openai_base_url",
        "authorization",
        "bearer ",
    )

    for value in forbidden:
        assert value not in extraction


def test_file_extraction_source_has_no_persistence_layer_reference():
    source = (read_file_route() + "\n" + read_file_extraction()).lower()

    forbidden = (
        "sqlalchemy",
        "database",
        "repository",
        "sqlite",
    )

    for value in forbidden:
        assert value not in source


def test_extraction_response_handling_uses_only_public_metadata():
    extraction = get_extract_file_function(read_app_js()).lower()

    forbidden = (
        "payload.file.path",
        "payload.file.provider",
        "payload.file.api_key",
        "payload.file.base_url",
        "payload.file.organization",
    )

    for value in forbidden:
        assert value not in extraction


# ---------------------------------------------------------------------------
# Result workspace remains available after document summarization
# ---------------------------------------------------------------------------


def test_document_summary_uses_existing_result_workspace():
    html = read_index_html()

    assert 'id="summaryText"' in html
    assert 'id="copySummaryButton"' in html
    assert 'id="downloadSummaryButton"' in html
    assert 'id="regenerateSummaryButton"' in html


def test_document_summary_uses_existing_processing_details():
    html = read_index_html()

    assert 'id="strategyValue"' in html
    assert 'id="chunkCountValue"' in html
    assert 'id="intelligenceModeValue"' in html
    assert 'id="observabilityStatusValue"' in html


def test_document_summary_result_is_rendered_from_canonical_response():
    js = read_app_js()
    submit_handler = get_submit_handler(js)

    assert "const payload = await response.json();" in submit_handler

    assert "summaryText.textContent = payload.summary;" in submit_handler

    assert "setUIState(UI_STATE.SUCCESS);" in submit_handler


# ---------------------------------------------------------------------------
# M7.3 complete architecture invariants
# ---------------------------------------------------------------------------


def test_m7_3_has_two_distinct_http_product_operations():
    js = read_app_js()

    assert '"/api/v1/files/extract"' in js

    assert 'fetch("/api/v1/summarize"' in js

    extraction = get_extract_file_function(js)

    assert "/api/v1/summarize" not in extraction


def test_m7_3_extracted_text_rejoins_canonical_source_workspace():
    js = read_app_js()

    extraction = get_extract_file_function(js)
    submit_handler = get_submit_handler(js)

    assert "inputText.value = payload.text;" in extraction

    assert "inputText.value.trim()" in submit_handler

    assert "text: normalizedText" in submit_handler


def test_m7_3_preserves_single_summarization_execution_path():
    js = read_app_js()
    route = read_ai_route()
    application = read_application()

    assert js.count('fetch("/api/v1/summarize"') == 1

    assert "SummarizationApplication" in route

    assert "class SummarizationApplication" in application

    extraction_boundary = read_file_route() + "\n" + read_file_extraction()

    assert "SummarizationApplication" not in extraction_boundary
