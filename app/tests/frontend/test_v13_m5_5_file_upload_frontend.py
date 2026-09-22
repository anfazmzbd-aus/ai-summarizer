from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INDEX_HTML = ROOT / "app" / "templates" / "index.html"
APP_JS = ROOT / "static" / "app.js"
STYLE_CSS = ROOT / "static" / "style.css"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_file_picker_contract_is_present():
    html = read(INDEX_HTML)

    assert 'id="fileInput"' in html
    assert 'type="file"' in html
    assert 'accept=".txt,.pdf,text/plain,application/pdf"' in html
    assert 'id="chooseFileButton"' in html


def test_drag_and_drop_contract_is_present():
    html = read(INDEX_HTML)
    javascript = read(APP_JS)

    assert 'id="fileDropZone"' in html
    assert 'tabindex="0"' in html
    assert 'role="button"' in html
    assert '"dragenter"' in javascript
    assert '"dragover"' in javascript
    assert '"dragleave"' in javascript
    assert '"drop"' in javascript
    assert "event.dataTransfer?.files" in javascript


def test_file_ingestion_has_accessible_status_and_error_regions():
    html = read(INDEX_HTML)

    assert 'id="fileStatus"' in html
    assert 'aria-live="polite"' in html
    assert 'id="fileError"' in html
    assert 'role="alert"' in html


def test_file_ingestion_calls_only_public_extraction_endpoint():
    javascript = read(APP_JS)

    assert '"/api/v1/files/extract"' in javascript
    assert 'formData.append("file", file)' in javascript


def test_file_ingestion_uses_multipart_form_data_without_manual_content_type():
    javascript = read(APP_JS)

    extraction_start = javascript.index("async function extractFile")
    extraction_end = javascript.index(
        "function handleSelectedFiles",
        extraction_start,
    )
    extraction_source = javascript[extraction_start:extraction_end]

    assert "new FormData()" in extraction_source
    assert 'method: "POST"' in extraction_source
    assert '"Content-Type"' not in extraction_source


def test_file_ingestion_supports_only_txt_and_pdf():
    javascript = read(APP_JS)

    assert 'Object.freeze([".txt", ".pdf"])' in javascript
    assert "Choose a TXT or PDF file." in javascript


def test_frontend_enforces_product_upload_limit():
    javascript = read(APP_JS)

    assert "10 * 1024 * 1024" in javascript
    assert "file.size > MAX_FILE_SIZE_BYTES" in javascript
    assert "The uploaded file exceeds the maximum allowed size." in javascript


def test_successful_extraction_replaces_source_text():
    javascript = read(APP_JS)

    assert "inputText.value = payload.text;" in javascript
    assert "updateInputState();" in javascript


def test_successful_extraction_preserves_existing_summary_controls():
    html = read(INDEX_HTML)

    assert 'id="summaryType"' in html
    assert 'id="summaryLength"' in html
    assert 'id="modelSelection"' in html
    assert 'id="customInstructions"' in html


def test_existing_summarization_endpoint_is_preserved():
    javascript = read(APP_JS)

    assert 'fetch("/api/v1/summarize"' in javascript
    assert "product_model: modelSelection.value" in javascript
    assert "summary_type: summaryType.value" in javascript
    assert "summary_length: summaryLength.value" in javascript


def test_file_extraction_does_not_construct_summary_request():
    javascript = read(APP_JS)

    extraction_start = javascript.index("async function extractFile")
    extraction_end = javascript.index(
        "function handleSelectedFiles",
        extraction_start,
    )
    extraction_source = javascript[extraction_start:extraction_end]

    assert "/api/v1/summarize" not in extraction_source
    assert "summary_type" not in extraction_source
    assert "summary_length" not in extraction_source
    assert "product_model" not in extraction_source
    assert "instructions" not in extraction_source


def test_extraction_loading_state_blocks_summarization():
    javascript = read(APP_JS)

    assert "let fileExtractionInProgress = false;" in javascript
    assert "fileExtractionInProgress ||" in javascript
    assert "setFileExtractionState(true);" in javascript
    assert "setFileExtractionState(false);" in javascript


def test_keyboard_file_picker_support_is_present():
    javascript = read(APP_JS)

    assert 'event.key === "Enter"' in javascript
    assert 'event.key === " "' in javascript
    assert "fileInput.click();" in javascript


def test_multiple_file_drop_is_rejected():
    javascript = read(APP_JS)

    assert "files.length > 1" in javascript
    assert "Upload one document at a time." in javascript


def test_file_metadata_is_presented_after_extraction():
    javascript = read(APP_JS)

    assert "buildFileStatusMessage" in javascript
    assert "fileMetadata.name" in javascript
    assert "fileMetadata.size_bytes" in javascript
    assert "fileMetadata.page_count" in javascript


def test_file_error_uses_safe_server_detail():
    javascript = read(APP_JS)

    assert 'typeof payload.detail === "string"' in javascript
    assert "The document could not be processed." in javascript


def test_file_clear_control_does_not_delete_source_text():
    javascript = read(APP_JS)

    start = javascript.index("clearFileButton.addEventListener(")
    end = javascript.index(
        'inputText.addEventListener("input"',
        start,
    )
    clear_source = javascript[start:end]

    assert "resetFileSelection();" in clear_source
    assert "inputText.value =" not in clear_source


def test_existing_input_metrics_contract_is_preserved():
    html = read(INDEX_HTML)
    javascript = read(APP_JS)

    assert 'id="wordCount"' in html
    assert 'id="characterCount"' in html
    assert "countWords(value)" in javascript
    assert "characterCount.textContent" in javascript


def test_file_ingestion_styles_are_present():
    stylesheet = read(STYLE_CSS)

    assert ".file-ingestion {" in stylesheet
    assert ".file-drop-zone {" in stylesheet
    assert ".file-drop-zone.is-dragging" in stylesheet
    assert ".file-status {" in stylesheet
    assert ".file-error {" in stylesheet
    assert ".visually-hidden {" in stylesheet


def test_existing_m4_viewport_density_contract_is_preserved():
    stylesheet = read(STYLE_CSS)

    assert "V13 M4 viewport-density refinement" in stylesheet
    assert "@media (min-width: 821px)" in stylesheet
    assert "#inputText" in stylesheet


def test_no_provider_configuration_is_added_to_file_ingestion():
    javascript = read(APP_JS)

    extraction_start = javascript.index("async function extractFile")
    extraction_end = javascript.index(
        "function handleSelectedFiles",
        extraction_start,
    )
    extraction_source = javascript[extraction_start:extraction_end].lower()

    assert "openai" not in extraction_source
    assert "provider" not in extraction_source
    assert "api_key" not in extraction_source
    assert "base_url" not in extraction_source
