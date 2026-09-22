from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

APP_JS = ROOT / "static" / "app.js"
FILE_EXTRACTION_ROUTE = ROOT / "app" / "routes" / "file_extraction.py"
SUMMARIZATION_ROUTE = ROOT / "app" / "routes" / "ai.py"
MAIN_APP = ROOT / "app" / "main.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extraction_function_source() -> str:
    javascript = read(APP_JS)

    start = javascript.index("async function extractFile")
    end = javascript.index(
        "function handleSelectedFiles",
        start,
    )

    return javascript[start:end]


def submit_handler_source() -> str:
    javascript = read(APP_JS)

    start = javascript.index("summaryForm.addEventListener(")

    return javascript[start:]


def test_file_extraction_uses_public_extraction_endpoint() -> None:
    source = extraction_function_source()

    assert '"/api/v1/files/extract"' in source
    assert 'method: "POST"' in source
    assert 'formData.append("file", file)' in source


def test_file_extraction_does_not_call_summarization_endpoint() -> None:
    source = extraction_function_source()

    assert "/api/v1/summarize" not in source


def test_file_extraction_does_not_send_summary_controls() -> None:
    source = extraction_function_source()

    assert "summary_type" not in source
    assert "summary_length" not in source
    assert "product_model" not in source
    assert "instructions" not in source


def test_extracted_text_rejoins_source_workspace() -> None:
    source = extraction_function_source()

    assert "inputText.value = payload.text;" in source
    assert "updateInputState();" in source


def test_extracted_text_is_not_automatically_summarized() -> None:
    source = extraction_function_source()

    assert "summaryForm.submit" not in source
    assert "summaryForm.requestSubmit" not in source
    assert "/api/v1/summarize" not in source


def test_summarization_reads_from_shared_source_workspace() -> None:
    source = submit_handler_source()

    assert ("const normalizedText = " "inputText.value.trim();") in source


def test_shared_source_text_is_sent_to_summarization() -> None:
    source = submit_handler_source()

    assert "text: normalizedText" in source


def test_summarization_uses_canonical_public_endpoint() -> None:
    source = submit_handler_source()

    assert 'fetch("/api/v1/summarize"' in source


def test_summary_type_survives_file_to_summary_transition() -> None:
    source = submit_handler_source()

    assert "summary_type: summaryType.value" in source


def test_summary_length_survives_file_to_summary_transition() -> None:
    source = submit_handler_source()

    assert "summary_length: summaryLength.value" in source


def test_product_model_survives_file_to_summary_transition() -> None:
    source = submit_handler_source()

    assert "product_model: modelSelection.value" in source


def test_custom_instructions_survive_file_to_summary_transition() -> None:
    source = submit_handler_source()

    assert ("instructions: " "customInstructions.value.trim() || null") in source


def test_uploaded_and_pasted_text_share_one_source_control() -> None:
    javascript = read(APP_JS)

    assert ("const inputText = " 'document.getElementById("inputText");') in javascript

    extraction_source = extraction_function_source()
    submit_source = submit_handler_source()

    assert "inputText.value = payload.text;" in extraction_source
    assert "inputText.value.trim()" in submit_source


def test_extraction_route_has_no_summarization_application_dependency() -> None:
    source = read(FILE_EXTRACTION_ROUTE)

    forbidden_terms = (
        "SummarizationApplication",
        "SummarizeRequest",
        "summarization_pipeline",
        "LLMRequest",
        "OpenAIProvider",
        "AI_PROVIDER",
        "OPENAI_API_KEY",
    )

    for term in forbidden_terms:
        assert term not in source


def test_extraction_route_has_no_provider_runtime_dependency() -> None:
    source = read(FILE_EXTRACTION_ROUTE).lower()

    forbidden_terms = (
        "openai",
        "provider_runtime",
        "llm_service",
        "prompt_manager",
    )

    for term in forbidden_terms:
        assert term not in source


def test_extraction_core_has_no_summarization_dependency() -> None:
    source = read(ROOT / "app" / "core" / "file_extraction.py")

    forbidden_terms = (
        "SummarizationApplication",
        "SummarizeRequest",
        "summarization_pipeline",
        "LLMRequest",
        "OpenAIProvider",
        "AI_PROVIDER",
        "OPENAI_API_KEY",
    )

    for term in forbidden_terms:
        assert term not in source


def test_extraction_core_has_no_provider_runtime_dependency() -> None:
    source = read(ROOT / "app" / "core" / "file_extraction.py").lower()

    forbidden_terms = (
        "openai",
        "provider_runtime",
        "llm_service",
        "prompt_manager",
    )

    for term in forbidden_terms:
        assert term not in source


def test_file_extraction_and_summarization_routes_are_both_registered() -> None:
    source = read(MAIN_APP)

    assert (
        "from app.routes.file_extraction " "import router as file_extraction_router"
    ) in source

    assert ("app.include_router(file_extraction_router)") in source

    assert ("from app.routes.ai import router as ai_router") in source

    assert "app.include_router(ai_router)" in source


def test_extraction_endpoint_remains_separate_from_summarization_route() -> None:
    extraction_source = read(FILE_EXTRACTION_ROUTE)

    assert 'prefix="/api/v1/files"' in extraction_source
    assert '"/extract"' in extraction_source

    assert '"/summarize"' not in extraction_source


def test_frontend_has_only_one_product_summarization_fetch() -> None:
    javascript = read(APP_JS)

    assert javascript.count('fetch("/api/v1/summarize"') == 1


def test_file_extraction_cannot_construct_provider_request() -> None:
    source = extraction_function_source().lower()

    forbidden_terms = (
        "provider:",
        "model:",
        "prompt:",
        "api_key",
        "base_url",
    )

    for term in forbidden_terms:
        assert term not in source


def test_file_extraction_response_becomes_editable_source_text() -> None:
    source = extraction_function_source()

    assignment_position = source.index("inputText.value = payload.text;")

    metrics_position = source.index(
        "updateInputState();",
        assignment_position,
    )

    assert assignment_position < metrics_position


def test_summarization_occurs_only_after_form_submission() -> None:
    source = submit_handler_source()

    fetch_position = source.index('fetch("/api/v1/summarize"')

    normalized_text_position = source.index("inputText.value.trim()")

    assert normalized_text_position < fetch_position


def test_summary_controls_are_evaluated_at_summarization_time() -> None:
    source = submit_handler_source()

    fetch_position = source.index('fetch("/api/v1/summarize"')

    request_source = source[fetch_position:]

    assert "product_model: modelSelection.value" in request_source
    assert "summary_type: summaryType.value" in request_source
    assert "summary_length: summaryLength.value" in request_source

    assert "customInstructions.value.trim() || null" in request_source


def test_extraction_failure_cannot_trigger_summarization() -> None:
    source = extraction_function_source()

    catch_position = source.index("} catch (extractionError) {")

    catch_source = source[catch_position:]

    assert "/api/v1/summarize" not in catch_source
    assert "summaryForm.submit" not in catch_source
    assert "summaryForm.requestSubmit" not in catch_source


def test_file_ingestion_preserves_user_control_over_summarization() -> None:
    javascript = read(APP_JS)

    assert ("summaryForm.addEventListener(\n" '    "submit",') in javascript

    assert ("chooseFileButton.addEventListener(") in javascript

    assert ("fileDropZone.addEventListener(") in javascript

    extraction_source = extraction_function_source()

    assert "/api/v1/summarize" not in extraction_source
