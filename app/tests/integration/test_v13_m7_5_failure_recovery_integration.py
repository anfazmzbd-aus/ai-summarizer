"""V13 M7.5 failure and recovery integration certification.

This suite certifies that product failures are contained safely and
that recoverable product state remains usable.

Certified failure/recovery areas:

    summarization validation failure
    unknown product model
    intelligence review requirement
    application/provider/runtime failure
    model configuration failure
    file validation failure
    TXT decoding failure
    PDF parsing failure
    duplicate-request prevention
    source preservation
    previous-result preservation
    retry/regeneration recovery
    product-safe error projection

M7.5 introduces no new product functionality.

Critical invariants:

* Internal implementation details never cross the product boundary.
* Unknown product model IDs never reach canonical application execution.
* A failed regeneration never destroys the previous successful result.
* Source text survives recoverable summarization failures.
* File extraction failures do not replace existing source text.
* File extraction remains independent from summarization.
* Loading state prevents duplicate summary execution.
* Regeneration uses the existing form submission path.
* Model-configuration failure fails closed.
* No failure path creates a second summarization endpoint.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.application import (
    ApplicationReviewRequiredError,
)
from app.core.product_model_catalogue import (
    ProductModel,
    ProductModelCatalogue,
)
from app.main import app
from app.routes import ai as ai_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"

AI_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "ai.py"

FILE_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "file_extraction.py"

FILE_EXTRACTION_PATH = PROJECT_ROOT / "app" / "core" / "file_extraction.py"


client = TestClient(app)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_index_html() -> str:
    return read(INDEX_HTML_PATH)


def read_app_js() -> str:
    return read(APP_JS_PATH)


def read_ai_route() -> str:
    return read(AI_ROUTE_PATH)


def read_file_route() -> str:
    return read(FILE_ROUTE_PATH)


def read_file_extraction() -> str:
    return read(FILE_EXTRACTION_PATH)


def get_submit_handler(js: str) -> str:
    start = js.index("summaryForm.addEventListener(")

    return js[start:]


def get_set_ui_state(js: str) -> str:
    start = js.index("function setUIState(")

    end = js.index(
        "function setModelState(",
        start,
    )

    return js[start:end]


def get_regenerate_function(js: str) -> str:
    start = js.index("function regenerateSummary()")

    end = js.index(
        "regenerateSummaryButton.addEventListener(",
        start,
    )

    return js[start:end]


def get_extract_file_function(js: str) -> str:
    start = js.index("async function extractFile(")

    end = js.index(
        "function handleSelectedFiles(",
        start,
    )

    return js[start:end]


def get_extraction_error_handler(
    extraction: str,
) -> str:
    start = extraction.index("catch (extractionError)")

    end = extraction.index(
        "finally",
        start,
    )

    return extraction[start:end]


def get_model_loader(js: str) -> str:
    start = js.index("async function loadProductModels()")

    end = js.index(
        "function getFileExtension(",
        start,
    )

    return js[start:end]


def build_catalogue() -> ProductModelCatalogue:
    return ProductModelCatalogue(
        (
            ProductModel(
                id="balanced",
                label="Balanced",
                provider="fake",
                model="runtime-balanced",
                is_default=True,
            ),
            ProductModel(
                id="quality",
                label="Quality",
                provider="fake",
                model="runtime-quality",
                is_default=False,
            ),
        )
    )


# ---------------------------------------------------------------------------
# Stable product error boundary
# ---------------------------------------------------------------------------


def test_ai_route_has_product_error_builder():
    route = read_ai_route()

    assert "def _product_error(" in route


def test_review_required_maps_to_product_error():
    route = read_ai_route()

    assert "except ApplicationReviewRequiredError:" in route

    assert 'code="REVIEW_REQUIRED"' in route


def test_invalid_application_state_maps_to_product_error():
    route = read_ai_route()

    assert "except ValueError:" in route

    assert 'code="INVALID_APPLICATION_STATE"' in route


def test_unexpected_failure_maps_to_product_error():
    route = read_ai_route()

    assert "except Exception:" in route

    assert 'code="SUMMARIZATION_FAILED"' in route


def test_review_required_returns_safe_409(
    monkeypatch,
):
    class ReviewApplication:
        async def summarize(
            self,
            request,
        ):
            raise ApplicationReviewRequiredError("private review implementation detail")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        ReviewApplication,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Review this request.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": {
            "error": {
                "code": "REVIEW_REQUIRED",
                "message": ("summarization requires review " "before execution"),
            }
        }
    }


def test_review_required_does_not_leak_internal_detail(
    monkeypatch,
):
    class ReviewApplication:
        async def summarize(
            self,
            request,
        ):
            raise ApplicationReviewRequiredError("private intelligence review state")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        ReviewApplication,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Review boundary.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert "private intelligence review state" not in response.text


def test_value_error_returns_safe_422(
    monkeypatch,
):
    class InvalidApplication:
        async def summarize(
            self,
            request,
        ):
            raise ValueError("private application authority state")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        InvalidApplication,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Invalid state.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"]["error"]["code"] == "INVALID_APPLICATION_STATE"

    assert (
        response.json()["detail"]["error"]["message"]
        == "summarization could not be authorized"
    )


def test_value_error_does_not_leak_internal_detail(
    monkeypatch,
):
    class InvalidApplication:
        async def summarize(
            self,
            request,
        ):
            raise ValueError("secret model authorization detail")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        InvalidApplication,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Invalid state.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert "secret model authorization detail" not in response.text


def test_runtime_failure_returns_safe_500(
    monkeypatch,
):
    class FailingApplication:
        async def summarize(
            self,
            request,
        ):
            raise RuntimeError("private provider stack trace")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        FailingApplication,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Runtime failure.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 500

    assert response.json()["detail"]["error"]["code"] == "SUMMARIZATION_FAILED"

    assert (
        response.json()["detail"]["error"]["message"]
        == "summarization could not be completed"
    )


def test_runtime_failure_does_not_leak_internal_detail(
    monkeypatch,
):
    class FailingApplication:
        async def summarize(
            self,
            request,
        ):
            raise RuntimeError("provider API key and stack trace detail")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        FailingApplication,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Runtime failure.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert "provider API key and stack trace detail" not in response.text


# ---------------------------------------------------------------------------
# Unknown product-model recovery boundary
# ---------------------------------------------------------------------------


def test_unknown_product_model_returns_422(
    monkeypatch,
):
    catalogue = build_catalogue()

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Unknown model request.",
            "product_model": "not-approved",
        },
    )

    assert response.status_code == 422


def test_unknown_product_model_has_safe_error_code(
    monkeypatch,
):
    catalogue = build_catalogue()

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Unknown model request.",
            "product_model": "not-approved",
        },
    )

    assert response.json()["detail"]["error"]["code"] == "INVALID_APPLICATION_STATE"


def test_unknown_product_model_has_safe_message(
    monkeypatch,
):
    catalogue = build_catalogue()

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Unknown model request.",
            "product_model": "not-approved",
        },
    )

    assert (
        response.json()["detail"]["error"]["message"]
        == "summarization could not be authorized"
    )


def test_unknown_product_model_does_not_leak_runtime_models(
    monkeypatch,
):
    catalogue = build_catalogue()

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Unknown model request.",
            "product_model": "not-approved",
        },
    )

    assert "runtime-balanced" not in response.text

    assert "runtime-quality" not in response.text


def test_unknown_product_model_does_not_leak_catalogue_exception(
    monkeypatch,
):
    catalogue = build_catalogue()

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Unknown model request.",
            "product_model": "not-approved",
        },
    )

    assert "unsupported product model" not in response.text


def test_unknown_product_model_never_reaches_application(
    monkeypatch,
):
    catalogue = build_catalogue()
    application_called = False

    class ApplicationMustNotRun:
        async def summarize(
            self,
            request,
        ):
            nonlocal application_called

            application_called = True

            raise AssertionError("application must not execute")

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        ApplicationMustNotRun,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Unknown model request.",
            "product_model": "not-approved",
        },
    )

    assert response.status_code == 422
    assert application_called is False


# ---------------------------------------------------------------------------
# Frontend summarization failure handling
# ---------------------------------------------------------------------------


def test_submit_handler_detects_non_success_response():
    submit = get_submit_handler(read_app_js())

    assert "if (!response.ok)" in submit


def test_submit_handler_attempts_safe_error_payload():
    submit = get_submit_handler(read_app_js())

    assert "payload.detail?.error?.message" in submit


def test_submit_handler_has_generic_failure_fallback():
    submit = get_submit_handler(read_app_js())

    assert "The summarization request failed." in submit


def test_submit_handler_enters_error_state():
    submit = get_submit_handler(read_app_js())

    assert "setUIState(UI_STATE.ERROR, message);" in submit


def test_request_error_handler_does_not_clear_source():
    submit = get_submit_handler(read_app_js())

    catch_start = submit.index("} catch (requestError) {")

    catch_source = submit[catch_start:]

    assert "inputText.value =" not in catch_source


def test_request_error_handler_does_not_clear_summary():
    submit = get_submit_handler(read_app_js())

    catch_start = submit.index("} catch (requestError) {")

    catch_source = submit[catch_start:]

    assert 'summaryText.textContent = ""' not in catch_source


def test_request_error_handler_does_not_show_empty_result():
    submit = get_submit_handler(read_app_js())

    catch_start = submit.index("} catch (requestError) {")

    catch_source = submit[catch_start:]

    assert "showEmptyResult();" not in catch_source


# ---------------------------------------------------------------------------
# UI failure-state preservation
# ---------------------------------------------------------------------------


def test_error_state_hides_loading_status():
    state = get_set_ui_state(read_app_js())

    error_start = state.index("if (nextState === UI_STATE.ERROR)")

    error_block = state[error_start:]

    assert "hideStatus();" in error_block


def test_error_state_displays_product_error():
    state = get_set_ui_state(read_app_js())

    error_start = state.index("if (nextState === UI_STATE.ERROR)")

    error_block = state[error_start:]

    assert "error.textContent" in error_block

    assert 'error.classList.remove("hidden")' in error_block


def test_error_state_stops_loading_button():
    state = get_set_ui_state(read_app_js())

    error_start = state.index("if (nextState === UI_STATE.ERROR)")

    error_block = state[error_start:]

    assert "setLoadingButton(false);" in error_block


def test_error_state_does_not_clear_rendered_summary():
    state = get_set_ui_state(read_app_js())

    error_start = state.index("if (nextState === UI_STATE.ERROR)")

    error_block = state[error_start:]

    assert "summaryText.textContent" not in error_block


def test_error_state_does_not_force_empty_result():
    state = get_set_ui_state(read_app_js())

    error_start = state.index("if (nextState === UI_STATE.ERROR)")

    error_block = state[error_start:]

    assert "showEmptyResult();" not in error_block


# ---------------------------------------------------------------------------
# Duplicate-request prevention
# ---------------------------------------------------------------------------


def test_submit_handler_blocks_duplicate_request_during_loading():
    submit = get_submit_handler(read_app_js())

    guard = submit[: submit.index("const normalizedText")]

    assert "currentState === UI_STATE.LOADING" in guard

    assert "return;" in guard


def test_submit_button_disabled_while_loading():
    js = read_app_js()

    start = js.index("function updateSubmitEligibility()")

    end = js.index(
        "function updateInputState()",
        start,
    )

    block = js[start:end]

    assert "currentState === UI_STATE.LOADING" in block


def test_result_actions_disabled_while_loading():
    js = read_app_js()

    start = js.index("function updateResultActionEligibility()")

    end = js.index(
        "function setCopySummaryStatus",
        start,
    )

    block = js[start:end]

    assert "currentState === UI_STATE.LOADING" in block

    assert "copySummaryButton.disabled" in block

    assert "downloadSummaryButton.disabled" in block

    assert "regenerateSummaryButton.disabled" in block


# ---------------------------------------------------------------------------
# Regeneration recovery
# ---------------------------------------------------------------------------


def test_regeneration_reuses_canonical_form_submission():
    regenerate = get_regenerate_function(read_app_js())

    assert "summaryForm.requestSubmit();" in regenerate


def test_regeneration_has_no_direct_fetch():
    regenerate = get_regenerate_function(read_app_js())

    assert "fetch(" not in regenerate


def test_regeneration_blocked_while_request_loading():
    regenerate = get_regenerate_function(read_app_js())

    assert "currentState === UI_STATE.LOADING" in regenerate


def test_regeneration_blocked_while_file_extraction_runs():
    regenerate = get_regenerate_function(read_app_js())

    assert "fileExtractionInProgress" in regenerate


def test_regeneration_requires_existing_result():
    regenerate = get_regenerate_function(read_app_js())

    assert "!hasSummaryResult()" in regenerate


def test_regeneration_requires_current_valid_source():
    regenerate = get_regenerate_function(read_app_js())

    assert "!hasValidInput()" in regenerate


def test_regeneration_requires_current_available_model():
    regenerate = get_regenerate_function(read_app_js())

    assert "!hasAvailableModel()" in regenerate


def test_failed_regeneration_preserves_existing_summary():
    submit = get_submit_handler(read_app_js())

    catch_start = submit.index("} catch (requestError) {")

    catch_source = submit[catch_start:]

    assert 'summaryText.textContent = ""' not in catch_source

    assert "showEmptyResult();" not in catch_source


def test_successful_retry_replaces_summary_on_success_path():
    submit = get_submit_handler(read_app_js())

    assert "summaryText.textContent = payload.summary;" in submit

    assert "setUIState(UI_STATE.SUCCESS);" in submit


def test_retry_uses_current_source():
    submit = get_submit_handler(read_app_js())

    assert "const normalizedText = inputText.value.trim();" in submit

    assert "text: normalizedText" in submit


def test_retry_uses_current_summary_controls():
    submit = get_submit_handler(read_app_js())

    assert "summary_type: summaryType.value" in submit

    assert "summary_length: summaryLength.value" in submit

    assert "customInstructions.value.trim() || null" in submit


def test_retry_uses_current_product_model():
    submit = get_submit_handler(read_app_js())

    assert "product_model: modelSelection.value" in submit


# ---------------------------------------------------------------------------
# Model configuration failure
# ---------------------------------------------------------------------------


def test_model_loader_checks_http_failure():
    loader = get_model_loader(read_app_js())

    assert "if (!response.ok)" in loader


def test_model_loader_validates_public_configuration():
    loader = get_model_loader(read_app_js())

    assert "validateProductModels(models)" in loader


def test_model_configuration_failure_clears_options():
    loader = get_model_loader(read_app_js())

    catch_start = loader.index("catch (configurationError)")

    catch_block = loader[catch_start:]

    assert "clearModelOptions();" in catch_block


def test_model_configuration_failure_sets_unavailable_option():
    loader = get_model_loader(read_app_js())

    catch_start = loader.index("catch (configurationError)")

    catch_block = loader[catch_start:]

    assert '"Models unavailable"' in catch_block


def test_model_configuration_failure_enters_error_state():
    loader = get_model_loader(read_app_js())

    catch_start = loader.index("catch (configurationError)")

    catch_block = loader[catch_start:]

    assert "MODEL_STATE.ERROR" in catch_block


def test_model_configuration_failure_fails_closed():
    js = read_app_js()

    assert "currentModelState === MODEL_STATE.READY" in js

    assert "modelSelection.value.trim().length > 0" in js


# ---------------------------------------------------------------------------
# File extraction API failures
# ---------------------------------------------------------------------------


def test_unsupported_file_type_returns_415():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "document.docx",
                b"not-supported",
                (
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                ),
            )
        },
    )

    assert response.status_code == 415


def test_mime_mismatch_returns_415():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "notes.txt",
                b"text",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 415


def test_invalid_utf8_returns_422():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "invalid.txt",
                b"\xff\xfe\xfa",
                "text/plain",
            )
        },
    )

    assert response.status_code == 422


def test_invalid_utf8_has_safe_message():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "invalid.txt",
                b"\xff\xfe\xfa",
                "text/plain",
            )
        },
    )

    assert response.json() == {"detail": ("Text files must use UTF-8 encoding.")}


def test_empty_txt_returns_422():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "empty.txt",
                b"   \r\n\t ",
                "text/plain",
            )
        },
    )

    assert response.status_code == 422


def test_invalid_pdf_returns_422():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "invalid.pdf",
                b"not actually a pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422


def test_invalid_pdf_has_safe_message():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "invalid.pdf",
                b"not actually a pdf",
                "application/pdf",
            )
        },
    )

    assert response.json() == {"detail": ("The PDF file could not be read.")}


# ---------------------------------------------------------------------------
# File extraction frontend recovery
# ---------------------------------------------------------------------------


def test_file_extraction_checks_http_failure():
    extraction = get_extract_file_function(read_app_js())

    assert "if (!response.ok)" in extraction


def test_file_extraction_uses_safe_server_detail():
    extraction = get_extract_file_function(read_app_js())

    assert 'typeof payload.detail === "string"' in extraction


def test_file_extraction_has_generic_failure_fallback():
    extraction = get_extract_file_function(read_app_js())

    assert "The document could not be processed." in extraction


def test_failed_file_extraction_clears_file_status():
    extraction = get_extract_file_function(read_app_js())

    error_handler = get_extraction_error_handler(extraction)

    assert "clearFileStatus();" in error_handler


def test_failed_file_extraction_displays_error():
    extraction = get_extract_file_function(read_app_js())

    error_handler = get_extraction_error_handler(extraction)

    assert "showFileError(message);" in error_handler


def test_failed_file_extraction_preserves_source_text():
    extraction = get_extract_file_function(read_app_js())

    error_handler = get_extraction_error_handler(extraction)

    assert "inputText.value" not in error_handler


def test_failed_file_extraction_releases_loading_state():
    extraction = get_extract_file_function(read_app_js())

    finally_start = extraction.index("finally")

    finally_block = extraction[finally_start:]

    assert "setFileExtractionState(false);" in finally_block


def test_file_extraction_failure_never_auto_summarizes():
    extraction = get_extract_file_function(read_app_js())

    assert "/api/v1/summarize" not in extraction

    assert "summaryForm.requestSubmit()" not in extraction


# ---------------------------------------------------------------------------
# Cross-path state independence
# ---------------------------------------------------------------------------


def test_file_error_path_does_not_clear_summary():
    extraction = get_extract_file_function(read_app_js())

    error_handler = get_extraction_error_handler(extraction)

    assert "summaryText.textContent" not in error_handler


def test_summary_error_path_does_not_clear_file_source():
    submit = get_submit_handler(read_app_js())

    catch_start = submit.index("} catch (requestError) {")

    catch_source = submit[catch_start:]

    assert "clearFileStatus();" not in catch_source

    assert "resetFileSelection();" not in catch_source


def test_file_and_summary_errors_have_separate_ui_channels():
    html = read_index_html()

    assert 'id="fileError"' in html
    assert 'id="error"' in html


def test_file_extraction_and_summarization_remain_separate_endpoints():
    js = read_app_js()

    assert '"/api/v1/files/extract"' in js

    assert 'fetch("/api/v1/summarize"' in js

    extraction = get_extract_file_function(js)

    assert "/api/v1/summarize" not in extraction


# ---------------------------------------------------------------------------
# Failure security boundaries
# ---------------------------------------------------------------------------


def test_frontend_failure_handling_does_not_reference_api_keys():
    js = read_app_js().lower()

    assert "openai_api_key" not in js


def test_frontend_failure_handling_does_not_reference_base_url():
    js = read_app_js().lower()

    assert "openai_base_url" not in js


def test_file_extraction_boundary_does_not_reference_provider_secrets():
    source = (read_file_route() + "\n" + read_file_extraction()).lower()

    forbidden = (
        "openai_api_key",
        "openai_base_url",
        "authorization",
        "bearer ",
    )

    for value in forbidden:
        assert value not in source


def test_ai_route_error_messages_are_product_safe():
    route = read_ai_route()

    assert "summarization requires review before execution" in route

    assert "summarization could not be authorized" in route

    assert "summarization could not be completed" in route


# ---------------------------------------------------------------------------
# Persistence boundary during failures
# ---------------------------------------------------------------------------


def test_failure_recovery_does_not_use_local_storage():
    js = read_app_js().lower()

    assert "localstorage" not in js


def test_failure_recovery_does_not_use_session_storage():
    js = read_app_js().lower()

    assert "sessionstorage" not in js


def test_failure_recovery_does_not_use_indexed_db():
    js = read_app_js().lower()

    assert "indexeddb" not in js


# ---------------------------------------------------------------------------
# M7.5 architecture invariants
# ---------------------------------------------------------------------------


def test_m7_5_preserves_single_summarization_fetch():
    js = read_app_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_m7_5_has_no_retry_endpoint():
    js = read_app_js().lower()

    forbidden = (
        "/api/v1/retry",
        "/api/v1/retry-summary",
        "/api/v1/resummarize",
        "/api/v1/regenerate",
    )

    for endpoint in forbidden:
        assert endpoint not in js


def test_m7_5_recovery_reuses_current_form_path():
    js = read_app_js()

    regenerate = get_regenerate_function(js)

    assert "summaryForm.requestSubmit();" in regenerate

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_m7_5_failure_does_not_destroy_previous_result():
    js = read_app_js()

    state = get_set_ui_state(js)

    error_start = state.index("if (nextState === UI_STATE.ERROR)")

    error_block = state[error_start:]

    submit = get_submit_handler(js)

    catch_start = submit.index("} catch (requestError) {")

    catch_block = submit[catch_start:]

    assert "showEmptyResult();" not in error_block

    assert "summaryText.textContent" not in error_block

    assert 'summaryText.textContent = ""' not in catch_block


def test_m7_5_file_failure_preserves_current_source():
    extraction = get_extract_file_function(read_app_js())

    error_handler = get_extraction_error_handler(extraction)

    assert "inputText.value" not in error_handler


def test_m7_5_model_failure_fails_closed():
    js = read_app_js()

    loader = get_model_loader(js)

    catch_start = loader.index("catch (configurationError)")

    catch_block = loader[catch_start:]

    assert "MODEL_STATE.ERROR" in catch_block

    assert '"Models unavailable"' in catch_block


def test_m7_5_failure_paths_do_not_create_persistence():
    js = read_app_js().lower()

    forbidden = (
        "localstorage",
        "sessionstorage",
        "indexeddb",
    )

    for value in forbidden:
        assert value not in js
