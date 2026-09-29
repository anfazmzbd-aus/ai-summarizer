"""V13 M8.5 error-state and edge-case UX hardening certification.

This suite audits failure recovery and unusual-but-valid interaction paths
in the frozen V13 product frontend.

Scope:
- duplicate-submit protection
- empty/whitespace source handling
- unavailable model handling
- product-config failure
- malformed model configuration
- file-selection edge cases
- unsupported and oversized uploads
- extraction transport/response failures
- extraction source preservation
- repeated file operations
- summarization HTTP and parsing failures
- malformed successful summary responses
- metadata fallbacks
- preservation of previous successful results
- clipboard failure handling
- download lifecycle safety
- regeneration guards
- stale-state cleanup
- loading-state consistency
- action eligibility recovery
- canonical execution-path preservation

M8.5 is deterministic and offline.
"""

from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"

STYLE_CSS_PATH = PROJECT_ROOT / "static" / "style.css"


def read(
    path: Path,
) -> str:
    return path.read_text(encoding="utf-8")


def read_html() -> str:
    return read(INDEX_HTML_PATH)


def read_js() -> str:
    return read(APP_JS_PATH)


def read_css() -> str:
    return read(STYLE_CSS_PATH)


def block_between(
    source: str,
    start_marker: str,
    end_marker: str,
) -> str:
    start = source.index(start_marker)

    end = source.index(
        end_marker,
        start + len(start_marker),
    )

    return source[start:end]


def submit_block(
    js: str,
) -> str:
    return js[js.index("summaryForm.addEventListener(") :]


def extraction_block(
    js: str,
) -> str:
    return block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )


# ---------------------------------------------------------------------------
# Source inventory
# ---------------------------------------------------------------------------


def test_m8_5_required_sources_exist():
    assert INDEX_HTML_PATH.is_file()
    assert APP_JS_PATH.is_file()
    assert STYLE_CSS_PATH.is_file()


def test_m8_5_javascript_is_non_empty():
    assert read_js().strip()


def test_m8_5_html_is_non_empty():
    assert read_html().strip()


def test_m8_5_css_is_non_empty():
    assert read_css().strip()


# ---------------------------------------------------------------------------
# UI state model
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "state",
    (
        "IDLE",
        "LOADING",
        "SUCCESS",
        "ERROR",
    ),
)
def test_ui_state_model_contains_required_state(
    state,
):
    js = read_js()

    assert f"{state}:" in js


def test_ui_state_has_explicit_current_state():
    js = read_js()

    assert "let currentState = UI_STATE.IDLE;" in js


def test_ui_state_is_applied_to_document_body():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    assert "document.body.dataset.uiState = nextState;" in block


def test_loading_state_has_visible_message():
    js = read_js()

    assert '"Generating summary..."' in js


def test_error_state_has_safe_fallback_message():
    js = read_js()

    assert '"The summarization request failed."' in js


# ---------------------------------------------------------------------------
# Empty and whitespace source handling
# ---------------------------------------------------------------------------


def test_submit_trims_source_before_validation():
    js = read_js()

    block = submit_block(js)

    assert "const normalizedText = inputText.value.trim();" in block


def test_empty_source_is_rejected_before_fetch():
    js = read_js()

    block = submit_block(js)

    empty_check = block.index("if (!normalizedText)")

    fetch_index = block.index('fetch("/api/v1/summarize"')

    assert empty_check < fetch_index


def test_empty_source_updates_input_state():
    js = read_js()

    block = submit_block(js)

    start = block.index("if (!normalizedText)")

    end = block.index("if (!hasAvailableModel())")

    empty_block = block[start:end]

    assert "updateInputState();" in empty_block


def test_empty_source_returns_focus_to_source():
    js = read_js()

    block = submit_block(js)

    start = block.index("if (!normalizedText)")

    end = block.index("if (!hasAvailableModel())")

    empty_block = block[start:end]

    assert "inputText.focus();" in empty_block


def test_empty_source_returns_without_request():
    js = read_js()

    block = submit_block(js)

    start = block.index("if (!normalizedText)")

    end = block.index("if (!hasAvailableModel())")

    empty_block = block[start:end]

    assert "return;" in empty_block


# ---------------------------------------------------------------------------
# Duplicate and concurrent submit protection
# ---------------------------------------------------------------------------


def test_duplicate_submit_is_guarded():
    js = read_js()

    block = submit_block(js)

    assert "if (currentState === UI_STATE.LOADING)" in block


def test_duplicate_submit_returns_immediately():
    js = read_js()

    block = submit_block(js)

    start = block.index("if (currentState === UI_STATE.LOADING)")

    normalized = block.index("const normalizedText")

    guard = block[start:normalized]

    assert "return;" in guard


def test_submit_button_is_disabled_during_loading():
    js = read_js()

    block = block_between(
        js,
        "function updateSubmitEligibility()",
        "function updateInputState()",
    )

    assert "currentState === UI_STATE.LOADING" in block


def test_submit_button_is_disabled_during_file_extraction():
    js = read_js()

    block = block_between(
        js,
        "function updateSubmitEligibility()",
        "function updateInputState()",
    )

    assert "fileExtractionInProgress" in block


# ---------------------------------------------------------------------------
# Product-model availability edge cases
# ---------------------------------------------------------------------------


def test_available_model_requires_ready_state():
    js = read_js()

    block = block_between(
        js,
        "function hasAvailableModel()",
        "function updateSubmitEligibility()",
    )

    assert "currentModelState === MODEL_STATE.READY" in block


def test_available_model_requires_non_empty_value():
    js = read_js()

    block = block_between(
        js,
        "function hasAvailableModel()",
        "function updateSubmitEligibility()",
    )

    assert "modelSelection.value.trim().length > 0" in block


def test_unavailable_model_blocks_submission():
    js = read_js()

    block = submit_block(js)

    assert "if (!hasAvailableModel())" in block


def test_unavailable_model_returns_focus_to_selector():
    js = read_js()

    block = submit_block(js)

    start = block.index("if (!hasAvailableModel())")

    loading = block.index(
        "setUIState(",
        start,
    )

    unavailable = block[start:loading]

    assert "modelSelection.focus();" in unavailable

    assert "return;" in unavailable


# ---------------------------------------------------------------------------
# Product-model configuration validation
# ---------------------------------------------------------------------------


def test_product_models_must_be_array():
    js = read_js()

    block = block_between(
        js,
        "function validateProductModels(",
        "async function loadProductModels()",
    )

    assert "Array.isArray(models)" in block


def test_product_models_cannot_be_empty():
    js = read_js()

    block = block_between(
        js,
        "function validateProductModels(",
        "async function loadProductModels()",
    )

    assert "models.length === 0" in block


def test_each_public_model_is_validated():
    js = read_js()

    block = block_between(
        js,
        "function validateProductModels(",
        "async function loadProductModels()",
    )

    assert "models.every(isValidPublicModel)" in block


@pytest.mark.parametrize(
    "field_check",
    (
        'typeof model.id === "string"',
        "model.id.trim().length > 0",
        'typeof model.label === "string"',
        "model.label.trim().length > 0",
        'typeof model.is_default === "boolean"',
    ),
)
def test_public_model_required_fields_are_validated(
    field_check,
):
    js = read_js()

    block = block_between(
        js,
        "function isValidPublicModel(",
        "function validateProductModels(",
    )

    assert field_check in block


def test_exactly_one_default_model_is_required():
    js = read_js()

    block = block_between(
        js,
        "function validateProductModels(",
        "async function loadProductModels()",
    )

    assert "return defaults.length === 1;" in block


def test_config_http_failure_is_rejected():
    js = read_js()

    block = block_between(
        js,
        "async function loadProductModels()",
        "function getFileExtension(",
    )

    assert "if (!response.ok)" in block


def test_invalid_product_config_is_rejected():
    js = read_js()

    block = block_between(
        js,
        "async function loadProductModels()",
        "function getFileExtension(",
    )

    assert "if (!validateProductModels(models))" in block


def test_failed_product_config_clears_options():
    js = read_js()

    block = block_between(
        js,
        "async function loadProductModels()",
        "function getFileExtension(",
    )

    catch_start = block.index("catch (configurationError)")

    catch_block = block[catch_start:]

    assert "clearModelOptions();" in catch_block


def test_failed_product_config_inserts_unavailable_option():
    js = read_js()

    block = block_between(
        js,
        "async function loadProductModels()",
        "function getFileExtension(",
    )

    catch_start = block.index("catch (configurationError)")

    catch_block = block[catch_start:]

    assert '"Models unavailable"' in catch_block


def test_failed_product_config_moves_model_state_to_error():
    js = read_js()

    block = block_between(
        js,
        "async function loadProductModels()",
        "function getFileExtension(",
    )

    catch_start = block.index("catch (configurationError)")

    catch_block = block[catch_start:]

    assert "MODEL_STATE.ERROR" in catch_block


# ---------------------------------------------------------------------------
# File-selection edge cases
# ---------------------------------------------------------------------------


def test_file_handler_ignores_missing_file_list():
    js = read_js()

    block = block_between(
        js,
        "function handleSelectedFiles(",
        "chooseFileButton.addEventListener(",
    )

    assert "!files" in block


def test_file_handler_ignores_empty_file_list():
    js = read_js()

    block = block_between(
        js,
        "function handleSelectedFiles(",
        "chooseFileButton.addEventListener(",
    )

    assert "files.length === 0" in block


def test_file_handler_blocks_during_existing_extraction():
    js = read_js()

    block = block_between(
        js,
        "function handleSelectedFiles(",
        "chooseFileButton.addEventListener(",
    )

    assert "fileExtractionInProgress" in block


def test_multiple_file_selection_is_rejected():
    js = read_js()

    block = block_between(
        js,
        "function handleSelectedFiles(",
        "chooseFileButton.addEventListener(",
    )

    assert "files.length > 1" in block


def test_multiple_file_selection_has_specific_message():
    js = read_js()

    assert '"Upload one document at a time."' in js


def test_single_selected_file_is_passed_to_extractor():
    js = read_js()

    block = block_between(
        js,
        "function handleSelectedFiles(",
        "chooseFileButton.addEventListener(",
    )

    assert "extractFile(files[0]);" in block


# ---------------------------------------------------------------------------
# Unsupported and oversized file handling
# ---------------------------------------------------------------------------


def test_supported_extensions_are_bounded():
    js = read_js()

    assert '[".txt", ".pdf"]' in js


def test_file_extension_check_normalizes_case():
    js = read_js()

    block = block_between(
        js,
        "function getFileExtension(",
        "function isSupportedFile(",
    )

    assert ".toLowerCase()" in block


def test_unsupported_file_is_rejected_before_fetch():
    js = read_js()

    block = extraction_block(js)

    unsupported = block.index("if (!isSupportedFile(file))")

    fetch_index = block.index('"/api/v1/files/extract"')

    assert unsupported < fetch_index


def test_unsupported_file_has_specific_message():
    js = read_js()

    assert '"Choose a TXT or PDF file."' in js


def test_file_size_limit_is_10_mib():
    js = read_js()

    assert "10 * 1024 * 1024" in js


def test_oversized_file_is_rejected_before_fetch():
    js = read_js()

    block = extraction_block(js)

    size_check = block.index("if (file.size > MAX_FILE_SIZE_BYTES)")

    fetch_index = block.index('"/api/v1/files/extract"')

    assert size_check < fetch_index


def test_oversized_file_has_safe_message():
    js = read_js()

    assert '"The uploaded file exceeds the maximum allowed size."' in js


# ---------------------------------------------------------------------------
# File extraction transport failures
# ---------------------------------------------------------------------------


def test_file_extraction_checks_http_status():
    js = read_js()

    block = extraction_block(js)

    assert "if (!response.ok)" in block


def test_file_extraction_handles_non_json_error_body():
    js = read_js()

    block = extraction_block(js)

    assert ".json()" in block

    assert ".catch(() => ({}))" in block


def test_file_extraction_uses_server_detail_when_available():
    js = read_js()

    block = extraction_block(js)

    assert 'typeof payload.detail === "string"' in block


def test_file_extraction_has_generic_error_fallback():
    js = read_js()

    assert '"The document could not be processed."' in js


def test_file_extraction_restores_loading_state_in_finally():
    js = read_js()

    block = extraction_block(js)

    assert "finally" in block

    assert "setFileExtractionState(false);" in block


# ---------------------------------------------------------------------------
# File extraction response validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "validation",
    (
        'typeof payload.text !== "string"',
        "payload.text.trim().length === 0",
        "payload.file === null",
        'typeof payload.file !== "object"',
        'typeof payload.file.name !== "string"',
        'typeof payload.file.type !== "string"',
        'typeof payload.file.size_bytes !== "number"',
    ),
)
def test_extraction_success_payload_is_validated(
    validation,
):
    js = read_js()

    block = extraction_block(js)

    assert validation in block


def test_invalid_extraction_response_has_specific_message():
    js = read_js()

    assert '"The document extraction response is invalid."' in js


def test_source_is_replaced_only_after_extraction_validation():
    js = read_js()

    block = extraction_block(js)

    validation = block.index('"The document extraction response is invalid."')

    replacement = block.index("inputText.value = payload.text;")

    assert replacement > validation


def test_successful_extraction_updates_input_state():
    js = read_js()

    block = extraction_block(js)

    assert "updateInputState();" in block


# ---------------------------------------------------------------------------
# File extraction preservation and cleanup
# ---------------------------------------------------------------------------


def test_failed_extraction_does_not_replace_source():
    js = read_js()

    block = extraction_block(js)

    catch_start = block.index("catch (extractionError)")

    finally_start = block.index(
        "finally",
        catch_start,
    )

    catch_block = block[catch_start:finally_start]

    assert "inputText.value =" not in catch_block


def test_failed_extraction_clears_stale_file_status():
    js = read_js()

    block = extraction_block(js)

    catch_start = block.index("catch (extractionError)")

    finally_start = block.index(
        "finally",
        catch_start,
    )

    catch_block = block[catch_start:finally_start]

    assert "clearFileStatus();" in catch_block


def test_failed_extraction_shows_error():
    js = read_js()

    block = extraction_block(js)

    catch_start = block.index("catch (extractionError)")

    finally_start = block.index(
        "finally",
        catch_start,
    )

    catch_block = block[catch_start:finally_start]

    assert "showFileError(message);" in catch_block


def test_new_extraction_clears_previous_file_error():
    js = read_js()

    block = extraction_block(js)

    assert "hideFileError();" in block


def test_clear_file_status_resets_file_input():
    js = read_js()

    block = block_between(
        js,
        "function clearFileStatus()",
        "function resetFileSelection()",
    )

    assert 'fileInput.value = "";' in block


def test_clear_file_status_resets_current_file_name():
    js = read_js()

    block = block_between(
        js,
        "function clearFileStatus()",
        "function resetFileSelection()",
    )

    assert "currentFileName = null;" in block


def test_reset_file_selection_clears_status_and_error():
    js = read_js()

    block = block_between(
        js,
        "function resetFileSelection()",
        "function formatFileSize(",
    )

    assert "clearFileStatus();" in block

    assert "hideFileError();" in block


# ---------------------------------------------------------------------------
# Summarization transport and server errors
# ---------------------------------------------------------------------------


def test_summarization_checks_http_status():
    js = read_js()

    block = submit_block(js)

    assert "if (!response.ok)" in block


def test_summarization_error_response_handles_invalid_json():
    js = read_js()

    block = submit_block(js)

    assert ".json()" in block

    assert ".catch(() => ({}))" in block


def test_server_error_message_is_used_when_present():
    js = read_js()

    block = submit_block(js)

    assert "payload.detail?.error?.message" in block


def test_server_error_has_safe_generic_fallback():
    js = read_js()

    block = submit_block(js)

    assert '"The summarization request failed."' in block


def test_network_or_parsing_error_enters_error_state():
    js = read_js()

    block = submit_block(js)

    catch_start = block.index("catch (requestError)")

    catch_block = block[catch_start:]

    assert "setUIState(UI_STATE.ERROR, message);" in catch_block


def test_non_error_throw_has_generic_message():
    js = read_js()

    block = submit_block(js)

    catch_start = block.index("catch (requestError)")

    catch_block = block[catch_start:]

    assert "requestError instanceof Error" in catch_block

    assert '"The summarization request failed."' in catch_block


# ---------------------------------------------------------------------------
# Successful summarization response integrity
# ---------------------------------------------------------------------------


def test_success_response_is_parsed_as_json():
    js = read_js()

    block = submit_block(js)

    assert "const payload = await response.json();" in block


def test_success_response_requires_string_summary():
    """A successful HTTP response must still contain a valid summary."""
    js = read_js()

    block = submit_block(js)

    assert 'typeof payload.summary !== "string"' in block


def test_success_response_rejects_blank_summary():
    """Blank summary content must not become a successful product state."""
    js = read_js()

    block = submit_block(js)

    assert "payload.summary.trim().length === 0" in block


def test_invalid_summary_response_has_safe_error_message():
    js = read_js()

    block = submit_block(js)

    assert '"The summarization response is invalid."' in block


def test_summary_is_assigned_only_after_success_validation():
    js = read_js()

    block = submit_block(js)

    validation = block.index('"The summarization response is invalid."')

    assignment = block.index("summaryText.textContent = payload.summary;")

    assert assignment > validation


# ---------------------------------------------------------------------------
# Metadata edge cases
# ---------------------------------------------------------------------------


def test_missing_metadata_uses_empty_object():
    js = read_js()

    block = submit_block(js)

    assert "const metadata = payload.metadata || {};" in block


@pytest.mark.parametrize(
    "fallback",
    (
        'metadata.strategy || "—"',
        'metadata.intelligence_mode || "—"',
        'metadata.observability_status || "—"',
    ),
)
def test_missing_text_metadata_uses_placeholder(
    fallback,
):
    js = read_js()

    assert fallback in js


def test_chunk_count_preserves_zero():
    js = read_js()

    assert 'metadata.chunk_count ?? "—"' in js


def test_metadata_is_written_with_text_content():
    js = read_js()

    for target in (
        "strategyValue.textContent",
        "chunkCountValue.textContent",
        "intelligenceModeValue.textContent",
        "observabilityStatusValue.textContent",
    ):
        assert target in js


# ---------------------------------------------------------------------------
# Previous result preservation
# ---------------------------------------------------------------------------


def test_loading_state_does_not_clear_existing_summary():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    loading_start = block.index("if (nextState === UI_STATE.LOADING)")

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    loading_block = block[loading_start:success_start]

    assert "summaryText.textContent =" not in loading_block


def test_error_state_does_not_clear_existing_summary():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    error_block = block[error_start:]

    assert "summaryText.textContent =" not in error_block


def test_error_state_does_not_hide_existing_result():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    error_block = block[error_start:]

    assert "showEmptyResult();" not in error_block


def test_loading_state_does_not_force_empty_result():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    loading_start = block.index("if (nextState === UI_STATE.LOADING)")

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    loading_block = block[loading_start:success_start]

    assert "showEmptyResult();" not in loading_block


# ---------------------------------------------------------------------------
# Clipboard edge cases
# ---------------------------------------------------------------------------


def test_copy_is_blocked_while_loading():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert "currentState === UI_STATE.LOADING" in block


def test_copy_is_blocked_without_summary():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert "!hasSummaryResult()" in block


def test_copy_clears_previous_copy_message():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert 'setCopySummaryStatus("");' in block


def test_copy_uses_only_summary_text():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert "navigator.clipboard.writeText(" in block

    assert "summaryText.textContent" in block


def test_copy_success_has_feedback():
    js = read_js()

    assert '"Summary copied."' in js


def test_copy_failure_is_caught():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert "catch (copyError)" in block


def test_copy_failure_has_feedback():
    js = read_js()

    assert '"Summary could not be copied."' in js


def test_new_success_clears_stale_copy_feedback():
    js = read_js()

    block = submit_block(js)

    assert 'setCopySummaryStatus("");' in block


# ---------------------------------------------------------------------------
# Download edge cases and resource cleanup
# ---------------------------------------------------------------------------


def test_download_is_blocked_while_loading():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "currentState === UI_STATE.LOADING" in block


def test_download_is_blocked_without_summary():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "!hasSummaryResult()" in block


def test_download_uses_utf8_plain_text_blob():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "text/plain;charset=utf-8" in block


def test_download_uses_summary_only():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "const summary = summaryText.textContent;" in block


def test_download_creates_object_url():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "URL.createObjectURL(blob)" in block


def test_download_link_is_hidden():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "downloadLink.hidden = true;" in block


def test_download_link_is_temporarily_added_to_document():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "document.body.appendChild(downloadLink);" in block


def test_download_cleanup_uses_finally():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "finally" in block


def test_download_removes_temporary_link():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "downloadLink.remove();" in block


def test_download_revokes_object_url():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "URL.revokeObjectURL(objectUrl);" in block


def test_download_filename_has_txt_extension():
    js = read_js()

    block = block_between(
        js,
        "function buildSummaryDownloadFileName(",
        "function downloadSummary()",
    )

    assert ".txt" in block


# ---------------------------------------------------------------------------
# Regeneration edge cases
# ---------------------------------------------------------------------------


def test_regeneration_is_blocked_while_loading():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "currentState === UI_STATE.LOADING" in block


def test_regeneration_is_blocked_during_file_extraction():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "fileExtractionInProgress" in block


def test_regeneration_requires_existing_summary():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "!hasSummaryResult()" in block


def test_regeneration_requires_valid_source():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "!hasValidInput()" in block


def test_regeneration_requires_available_model():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "!hasAvailableModel()" in block


def test_regeneration_returns_when_guard_fails():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "return;" in block


def test_regeneration_uses_canonical_form_submission():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "summaryForm.requestSubmit();" in block


def test_regeneration_does_not_create_second_fetch():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "fetch(" not in block


# ---------------------------------------------------------------------------
# Result-action eligibility recovery
# ---------------------------------------------------------------------------


def test_result_action_state_depends_on_summary_presence():
    js = read_js()

    block = block_between(
        js,
        "function updateResultActionEligibility()",
        "function setCopySummaryStatus(",
    )

    assert "!hasSummaryResult()" in block


def test_copy_and_download_share_loading_guard():
    js = read_js()

    block = block_between(
        js,
        "function updateResultActionEligibility()",
        "function setCopySummaryStatus(",
    )

    assert "const actionsDisabled =" in block

    assert "copySummaryButton.disabled = actionsDisabled;" in block

    assert "downloadSummaryButton.disabled = actionsDisabled;" in block


def test_regenerate_has_stricter_eligibility():
    js = read_js()

    block = block_between(
        js,
        "function updateResultActionEligibility()",
        "function setCopySummaryStatus(",
    )

    assert "regenerateSummaryButton.disabled =" in block

    assert "fileExtractionInProgress" in block

    assert "!hasValidInput()" in block

    assert "!hasAvailableModel()" in block


def test_file_extraction_state_refreshes_result_actions():
    js = read_js()

    block = block_between(
        js,
        "function setFileExtractionState(",
        "function hideFileError()",
    )

    assert "updateResultActionEligibility();" in block


def test_ui_state_refreshes_result_actions():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    assert "updateResultActionEligibility();" in block


def test_model_state_refreshes_result_actions():
    js = read_js()

    block = block_between(
        js,
        "function setModelState(",
        "function clearModelOptions()",
    )

    assert "updateResultActionEligibility();" in block


def test_model_change_refreshes_result_actions():
    js = read_js()

    block = block_between(
        js,
        "modelSelection.addEventListener(",
        "function hasSummaryResult()",
    )

    assert "updateResultActionEligibility();" in block


# ---------------------------------------------------------------------------
# Stale-state cleanup
# ---------------------------------------------------------------------------


def test_loading_clears_previous_summary_error():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    loading_start = block.index("if (nextState === UI_STATE.LOADING)")

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    loading_block = block[loading_start:success_start]

    assert "hideError();" in loading_block


def test_success_clears_status_and_error():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    success_block = block[success_start:error_start]

    assert "hideStatus();" in success_block

    assert "hideError();" in success_block


def test_error_clears_loading_status():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    error_block = block[error_start:]

    assert "hideStatus();" in error_block


def test_loading_clears_stale_copy_status():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    loading_start = block.index("if (nextState === UI_STATE.LOADING)")

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    loading_block = block[loading_start:success_start]

    assert 'setCopySummaryStatus("");' in loading_block


# ---------------------------------------------------------------------------
# Error-state visibility
# ---------------------------------------------------------------------------


def test_summary_error_region_exists():
    html = read_html()

    assert 'id="error"' in html

    assert 'role="alert"' in html


def test_file_error_region_exists():
    html = read_html()

    assert 'id="fileError"' in html


def test_errors_are_text_content_not_inner_html():
    js = read_js()

    assert "error.innerHTML" not in js

    assert "fileError.innerHTML" not in js


def test_server_error_is_not_rendered_with_inner_html():
    js = read_js()

    assert ".innerHTML =" not in submit_block(js)


# ---------------------------------------------------------------------------
# Initialization edge cases
# ---------------------------------------------------------------------------


def test_initial_input_state_is_computed():
    js = read_js()

    assert "updateInputState();" in js


def test_initial_instruction_count_is_computed():
    js = read_js()

    assert "updateInstructionsCount();" in js


def test_initial_ui_state_is_idle():
    js = read_js()

    assert "setUIState(UI_STATE.IDLE);" in js


def test_product_models_are_loaded_after_initial_state_setup():
    js = read_js()

    idle = js.rindex("setUIState(UI_STATE.IDLE);")

    models = js.rindex("loadProductModels();")

    assert models > idle


# ---------------------------------------------------------------------------
# Architecture and product-scope invariants
# ---------------------------------------------------------------------------


def test_exactly_one_summarization_fetch_exists():
    js = read_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_exactly_one_file_extraction_endpoint_reference_exists():
    js = read_js()

    assert js.count('"/api/v1/files/extract"') == 1


def test_product_config_endpoint_is_preserved():
    js = read_js()

    assert '"/api/v1/product-config"' in js


def test_file_extraction_does_not_summarize():
    js = read_js()

    block = extraction_block(js)

    assert "/api/v1/summarize" not in block


def test_download_does_not_call_server():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "fetch(" not in block


def test_copy_does_not_call_server():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert "fetch(" not in block


# ---------------------------------------------------------------------------
# No persistence/history introduced
# ---------------------------------------------------------------------------


def test_frontend_does_not_use_local_storage():
    js = read_js()

    assert "localStorage" not in js


def test_frontend_does_not_use_session_storage():
    js = read_js()

    assert "sessionStorage" not in js


def test_frontend_does_not_use_indexed_db():
    js = read_js()

    assert "indexedDB" not in js


def test_frontend_does_not_use_cookie_persistence():
    js = read_js()

    assert "document.cookie" not in js


# ---------------------------------------------------------------------------
# Defensive text rendering
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "target",
    (
        "summaryText",
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
        "error",
        "fileError",
        "fileStatusText",
        "copySummaryStatus",
        "modelSelectionStatus",
    ),
)
def test_dynamic_product_text_does_not_use_inner_html(
    target,
):
    js = read_js()

    assert f"{target}.innerHTML" not in js


# ---------------------------------------------------------------------------
# M8.5 deterministic/offline boundary
# ---------------------------------------------------------------------------


def test_m8_5_has_no_live_pytest_marker():
    source = Path(__file__).read_text(encoding="utf-8")

    assert "pytest.mark." + "live" not in source


def test_m8_5_requires_no_external_provider():
    source = Path(__file__).read_text(encoding="utf-8")

    forbidden = (
        "openai" + ".com",
        "openrouter" + ".ai",
        "OPENAI" + "_API_KEY",
        "OPENROUTER" + "_API_KEY",
    )

    for value in forbidden:
        assert value not in source


def test_m8_5_is_frontend_scoped():
    assert APP_JS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/app.js"

    assert (
        INDEX_HTML_PATH.relative_to(PROJECT_ROOT).as_posix()
        == "app/templates/index.html"
    )
