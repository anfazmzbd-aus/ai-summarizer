"""V13 M7.4 controls, model, and result-workspace integration certification.

This suite certifies the cross-component product workflow connecting:

    source
        + summary type
        + summary length
        + custom instructions
        + approved product model
        -> POST /api/v1/summarize
        -> server-side product-model resolution
        -> SummarizationApplication
        -> product-safe response
        -> result workspace
        -> copy / TXT download / regenerate / safe details

M7.4 introduces no new product functionality.

Critical invariants:

* Product controls remain product-facing inputs.
* The browser sends only the selected public product-model identifier.
* Private provider/runtime mappings remain server-side.
* Model resolution occurs before canonical application execution.
* Result actions operate on the rendered successful summary.
* Regeneration reuses the canonical summary form submission.
* No second summarization path is introduced.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.product_model_catalogue import (
    ProductModel,
    ProductModelCatalogue,
)
from app.main import app
from app.routes import ai as ai_route
from app.routes import product_config as product_config_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"

AI_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "ai.py"

PRODUCT_CONFIG_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "product_config.py"

PRODUCT_MODEL_CATALOGUE_PATH = (
    PROJECT_ROOT / "app" / "core" / "product_model_catalogue.py"
)

APPLICATION_PATH = PROJECT_ROOT / "app" / "api" / "application.py"


client = TestClient(app)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_index_html() -> str:
    return read(INDEX_HTML_PATH)


def read_app_js() -> str:
    return read(APP_JS_PATH)


def read_ai_route() -> str:
    return read(AI_ROUTE_PATH)


def read_product_config_route() -> str:
    return read(PRODUCT_CONFIG_ROUTE_PATH)


def read_product_model_catalogue() -> str:
    return read(PRODUCT_MODEL_CATALOGUE_PATH)


def read_application() -> str:
    return read(APPLICATION_PATH)


def get_submit_handler(js: str) -> str:
    start = js.index("summaryForm.addEventListener(")

    return js[start:]


def get_regenerate_function(js: str) -> str:
    start = js.index("function regenerateSummary()")

    end = js.index(
        "regenerateSummaryButton.addEventListener(",
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


def get_model_loader(js: str) -> str:
    start = js.index("async function loadProductModels()")

    end = js.index(
        "inputText.addEventListener(",
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


class FakeMetadata:
    strategy = "direct"
    chunk_count = 1
    intelligence_mode = "preserve"
    trace_id = "m7-4-trace"
    explainability_summary = "preserved"
    attributes = {}


class FakeResult:
    def __init__(
        self,
        *,
        model: str,
        summary: str = "M7.4 certified summary",
    ) -> None:
        self.summary = summary
        self.model = model
        self.prompt_tokens = 20
        self.completion_tokens = 30
        self.metadata = FakeMetadata()

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


# ---------------------------------------------------------------------------
# Product-control workspace
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


def test_model_selection_control_exists():
    html = read_index_html()

    assert 'id="modelSelection"' in html


def test_controls_are_inside_summary_form():
    html = read_index_html()

    form_start = html.index('id="summaryForm"')

    form_end = html.index(
        "</form>",
        form_start,
    )

    form = html[form_start:form_end]

    assert 'id="inputText"' in form
    assert 'id="summaryType"' in form
    assert 'id="summaryLength"' in form
    assert 'id="customInstructions"' in form
    assert 'id="modelSelection"' in form


# ---------------------------------------------------------------------------
# Control values -> canonical request
# ---------------------------------------------------------------------------


def test_request_uses_current_source():
    submit = get_submit_handler(read_app_js())

    assert "inputText.value.trim()" in submit

    assert "text: normalizedText" in submit


def test_request_uses_current_summary_type():
    submit = get_submit_handler(read_app_js())

    assert "summary_type: summaryType.value" in submit


def test_request_uses_current_summary_length():
    submit = get_submit_handler(read_app_js())

    assert "summary_length: summaryLength.value" in submit


def test_request_uses_current_custom_instructions():
    submit = get_submit_handler(read_app_js())

    assert "instructions:" in submit

    assert "customInstructions.value.trim() || null" in submit


def test_request_uses_current_public_product_model():
    submit = get_submit_handler(read_app_js())

    assert "product_model: modelSelection.value" in submit


def test_all_product_controls_share_one_request_body():
    submit = get_submit_handler(read_app_js())

    body_start = submit.index("body: JSON.stringify({")

    body_end = submit.index(
        "}),",
        body_start,
    )

    body = submit[body_start:body_end]

    assert "text: normalizedText" in body

    assert "product_model: modelSelection.value" in body

    assert "summary_type: summaryType.value" in body

    assert "summary_length: summaryLength.value" in body

    assert "customInstructions.value.trim() || null" in body


def test_controls_use_single_summarization_fetch():
    js = read_app_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_control_request_is_json_post():
    submit = get_submit_handler(read_app_js())

    assert 'method: "POST"' in submit

    assert '"Content-Type": "application/json"' in submit


# ---------------------------------------------------------------------------
# Public product-model configuration
# ---------------------------------------------------------------------------


def test_frontend_loads_public_product_configuration():
    js = read_app_js()

    assert '"/api/v1/product-config"' in js


def test_product_config_route_is_registered():
    paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/product-config" in paths


def test_model_loader_reads_public_models():
    loader = get_model_loader(read_app_js())

    assert "const models = payload.models;" in loader


def test_frontend_uses_public_model_id_as_option_value():
    js = read_app_js()

    assert "option.value = model.id;" in js


def test_frontend_uses_public_model_label():
    js = read_app_js()

    assert "option.textContent = model.label;" in js


def test_frontend_honors_server_default_model():
    js = read_app_js()

    assert "if (model.is_default)" in js

    assert "option.selected = true;" in js


def test_frontend_requires_exactly_one_default_model():
    js = read_app_js()

    assert "defaults.length === 1" in js


def test_frontend_does_not_construct_runtime_model_mapping():
    js = read_app_js()

    forbidden = (
        "model.provider",
        "model.runtime_model",
        "model.api_key",
        "model.base_url",
    )

    for value in forbidden:
        assert value not in js


# ---------------------------------------------------------------------------
# Public configuration safety
# ---------------------------------------------------------------------------


def test_product_config_exposes_public_model_fields_only(
    monkeypatch,
):
    catalogue = build_catalogue()

    monkeypatch.setattr(
        product_config_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.get("/api/v1/product-config")

    assert response.status_code == 200

    assert response.json() == {
        "models": [
            {
                "id": "balanced",
                "label": "Balanced",
                "is_default": True,
            },
            {
                "id": "quality",
                "label": "Quality",
                "is_default": False,
            },
        ]
    }


def test_product_config_does_not_expose_runtime_models(
    monkeypatch,
):
    catalogue = build_catalogue()

    monkeypatch.setattr(
        product_config_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.get("/api/v1/product-config")

    serialized = response.text

    assert "runtime-balanced" not in serialized

    assert "runtime-quality" not in serialized


def test_product_config_does_not_expose_provider(
    monkeypatch,
):
    catalogue = build_catalogue()

    monkeypatch.setattr(
        product_config_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.get("/api/v1/product-config")

    assert '"provider"' not in response.text


def test_product_config_source_has_product_safe_response():
    source = read_product_config_route()

    assert "ProductConfigResponse" in source

    assert "ProductModelOption" in source


# ---------------------------------------------------------------------------
# Server-side model catalogue
# ---------------------------------------------------------------------------


def test_product_model_catalogue_contains_private_runtime_mapping():
    source = read_product_model_catalogue()

    assert "class ProductModel:" in source

    assert "provider: str" in source
    assert "model: str" in source


def test_product_model_catalogue_resolves_public_id():
    catalogue = build_catalogue()

    resolved = catalogue.resolve("quality")

    assert resolved.id == "quality"

    assert resolved.provider == "fake"

    assert resolved.model == "runtime-quality"


def test_product_model_catalogue_rejects_unknown_id():
    catalogue = build_catalogue()

    try:
        catalogue.resolve("not-approved")
    except ValueError as error:
        assert str(error) == "unsupported product model"
    else:
        raise AssertionError("unknown product model was accepted")


def test_catalogue_requires_exactly_one_default():
    source = read_product_model_catalogue()

    assert "product model catalogue must contain exactly one default" in source


def test_catalogue_requires_unique_product_ids():
    source = read_product_model_catalogue()

    assert "product model ids must be unique" in source


# ---------------------------------------------------------------------------
# Server resolution -> canonical application
# ---------------------------------------------------------------------------


def test_ai_route_references_product_model_catalogue():
    route = read_ai_route()

    assert "build_product_model_catalogue" in route


def test_ai_route_references_summarization_application():
    route = read_ai_route()

    assert "SummarizationApplication" in route


def test_canonical_application_exists():
    application = read_application()

    assert "class SummarizationApplication" in application


def test_approved_product_model_is_resolved_before_application(
    monkeypatch,
):
    catalogue = build_catalogue()
    captured = {}

    class FakeApplication:
        async def summarize(
            self,
            request,
        ):
            captured["request"] = request

            return FakeResult(
                model=request.model or "",
            )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": ("M7.4 integration source text " "for approved model resolution."),
            "product_model": "quality",
            "summary_type": "executive",
            "summary_length": "short",
            "instructions": ("Emphasize operational impact."),
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.provider == "fake"

    assert request.model == "runtime-quality"


def test_product_controls_reach_application_request(
    monkeypatch,
):
    catalogue = build_catalogue()
    captured = {}

    class FakeApplication:
        async def summarize(
            self,
            request,
        ):
            captured["request"] = request

            return FakeResult(
                model=request.model or "",
            )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    source = "Product controls must cross " "the canonical boundary."

    instructions = "Retain concrete decisions."

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": source,
            "product_model": "balanced",
            "summary_type": "key_points",
            "summary_length": "detailed",
            "instructions": instructions,
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.text == source

    assert request.provider == "fake"

    assert request.model == "runtime-balanced"

    assert request.summary_type.value == "key_points"

    assert request.summary_length.value == "detailed"

    assert request.instructions == instructions


def test_unknown_product_model_does_not_reach_application(
    monkeypatch,
):
    catalogue = build_catalogue()
    application_called = False

    class FakeApplication:
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
        lambda: FakeApplication(),
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": ("Unknown models must fail " "before application execution."),
            "product_model": "not-approved",
            "summary_type": "general",
            "summary_length": "medium",
        },
    )

    assert response.status_code == 422

    assert application_called is False


# ---------------------------------------------------------------------------
# Result response -> result workspace
# ---------------------------------------------------------------------------


def test_successful_response_is_parsed_once():
    submit = get_submit_handler(read_app_js())

    assert "const payload = await response.json();" in submit


def test_successful_summary_populates_result_workspace():
    submit = get_submit_handler(read_app_js())

    assert "summaryText.textContent = payload.summary;" in submit


def test_successful_response_uses_product_safe_metadata_object():
    submit = get_submit_handler(read_app_js())

    assert "const metadata = payload.metadata || {};" in submit


def test_strategy_metadata_populates_result_details():
    submit = get_submit_handler(read_app_js())

    assert "metadata.strategy" in submit


def test_chunk_count_metadata_populates_result_details():
    submit = get_submit_handler(read_app_js())

    assert "metadata.chunk_count" in submit


def test_intelligence_mode_metadata_populates_result_details():
    submit = get_submit_handler(read_app_js())

    assert "metadata.intelligence_mode" in submit


def test_observability_status_metadata_populates_result_details():
    submit = get_submit_handler(read_app_js())

    assert "metadata.observability_status" in submit


def test_successful_result_enters_success_state():
    submit = get_submit_handler(read_app_js())

    assert "setUIState(UI_STATE.SUCCESS);" in submit


def test_successful_result_receives_focus():
    submit = get_submit_handler(read_app_js())

    assert "summaryContent.focus();" in submit


# ---------------------------------------------------------------------------
# Result workspace controls
# ---------------------------------------------------------------------------


def test_copy_control_exists():
    html = read_index_html()

    assert 'id="copySummaryButton"' in html


def test_download_control_exists():
    html = read_index_html()

    assert 'id="downloadSummaryButton"' in html


def test_regenerate_control_exists():
    html = read_index_html()

    assert 'id="regenerateSummaryButton"' in html


def test_processing_details_exist():
    html = read_index_html()

    assert '<details class="result-details">' in html


def test_processing_details_are_collapsed_by_default():
    html = read_index_html()

    start = html.index('<details class="result-details">')

    end = html.index(
        ">",
        start,
    )

    opening_tag = html[start : end + 1]

    assert " open" not in opening_tag


# ---------------------------------------------------------------------------
# Copy integration
# ---------------------------------------------------------------------------


def test_copy_uses_rendered_summary_only():
    js = read_app_js()

    assert "navigator.clipboard.writeText" in js

    assert "summaryText.textContent" in js


def test_copy_does_not_use_source_text():
    js = read_app_js()

    start = js.index("async function copySummary()")

    end = js.index(
        "copySummaryButton.addEventListener(",
        start,
    )

    copy_function = js[start:end]

    assert "inputText.value" not in copy_function

    assert "customInstructions.value" not in copy_function


# ---------------------------------------------------------------------------
# Download integration
# ---------------------------------------------------------------------------


def test_download_uses_rendered_summary():
    download = get_download_function(read_app_js())

    assert "summaryText.textContent" in download


def test_download_is_plain_text_utf8():
    download = get_download_function(read_app_js())

    assert "text/plain;charset=utf-8" in download


def test_download_is_browser_side():
    download = get_download_function(read_app_js())

    assert "new Blob(" in download

    assert "URL.createObjectURL" in download

    assert "URL.revokeObjectURL" in download


def test_download_does_not_call_backend():
    download = get_download_function(read_app_js())

    assert "fetch(" not in download


# ---------------------------------------------------------------------------
# Regeneration integration
# ---------------------------------------------------------------------------


def test_regenerate_reuses_summary_form_submission():
    regenerate = get_regenerate_function(read_app_js())

    assert "summaryForm.requestSubmit();" in regenerate


def test_regenerate_does_not_call_backend_directly():
    regenerate = get_regenerate_function(read_app_js())

    assert "fetch(" not in regenerate


def test_regenerate_requires_existing_summary():
    regenerate = get_regenerate_function(read_app_js())

    assert "!hasSummaryResult()" in regenerate


def test_regenerate_requires_valid_current_source():
    regenerate = get_regenerate_function(read_app_js())

    assert "!hasValidInput()" in regenerate


def test_regenerate_requires_available_model():
    regenerate = get_regenerate_function(read_app_js())

    assert "!hasAvailableModel()" in regenerate


def test_regenerate_is_blocked_during_loading():
    regenerate = get_regenerate_function(read_app_js())

    assert "currentState === UI_STATE.LOADING" in regenerate


def test_regenerate_is_blocked_during_file_extraction():
    regenerate = get_regenerate_function(read_app_js())

    assert "fileExtractionInProgress" in regenerate


def test_regeneration_reuses_current_controls():
    js = read_app_js()

    regenerate = get_regenerate_function(js)

    submit = get_submit_handler(js)

    assert "summaryForm.requestSubmit();" in regenerate

    assert "summaryType.value" in submit

    assert "summaryLength.value" in submit

    assert "customInstructions.value.trim()" in submit

    assert "modelSelection.value" in submit


# ---------------------------------------------------------------------------
# Security boundary
# ---------------------------------------------------------------------------


def test_result_workspace_does_not_render_provider_credentials():
    js = read_app_js().lower()
    html = read_index_html().lower()

    forbidden = (
        "openai_api_key",
        "api_key",
        "openai_base_url",
        "authorization: bearer",
    )

    for value in forbidden:
        assert value not in js
        assert value not in html


def test_result_details_do_not_render_runtime_model_mapping():
    submit = get_submit_handler(read_app_js()).lower()

    forbidden = (
        "metadata.provider",
        "metadata.api_key",
        "metadata.base_url",
        "metadata.prompt",
        "metadata.system_prompt",
    )

    for value in forbidden:
        assert value not in submit


def test_frontend_never_resolves_product_model_to_provider():
    js = read_app_js()

    assert "model.provider" not in js

    assert "model.runtime_model" not in js


# ---------------------------------------------------------------------------
# Persistence boundary
# ---------------------------------------------------------------------------


def test_controls_and_results_are_not_persisted_locally():
    js = read_app_js().lower()

    forbidden = (
        "localstorage",
        "sessionstorage",
        "indexeddb",
    )

    for value in forbidden:
        assert value not in js


def test_no_result_history_endpoint_is_used():
    js = read_app_js().lower()

    forbidden = (
        "/api/v1/history",
        "/api/v1/results",
        "/api/v1/summaries/history",
    )

    for endpoint in forbidden:
        assert endpoint not in js


# ---------------------------------------------------------------------------
# M7.4 complete integration invariants
# ---------------------------------------------------------------------------


def test_m7_4_controls_share_single_canonical_request():
    js = read_app_js()
    submit = get_submit_handler(js)

    assert js.count('fetch("/api/v1/summarize"') == 1

    assert "text: normalizedText" in submit

    assert "product_model: modelSelection.value" in submit

    assert "summary_type: summaryType.value" in submit

    assert "summary_length: summaryLength.value" in submit

    assert "customInstructions.value.trim() || null" in submit


def test_m7_4_model_resolution_remains_server_side():
    js = read_app_js()
    route = read_ai_route()
    catalogue = read_product_model_catalogue()

    assert "product_model: modelSelection.value" in js

    assert "build_product_model_catalogue" in route

    assert "def resolve(" in catalogue

    assert "model.provider" not in js

    assert "model.runtime_model" not in js


def test_m7_4_result_actions_share_rendered_summary():
    js = read_app_js()

    assert "summaryText.textContent" in js

    assert "navigator.clipboard.writeText" in js

    assert "new Blob(" in js

    regenerate = get_regenerate_function(js)

    assert "summaryForm.requestSubmit();" in regenerate


def test_m7_4_preserves_canonical_application_boundary():
    js = read_app_js()
    route = read_ai_route()
    application = read_application()

    assert js.count('fetch("/api/v1/summarize"') == 1

    assert "SummarizationApplication" in route

    assert "class SummarizationApplication" in application

    assert "summarization_pipeline" not in js.lower()

    assert "bounded_intelligence" not in js.lower()


def test_m7_4_has_no_alternate_regeneration_endpoint():
    js = read_app_js().lower()

    forbidden = (
        "/api/v1/regenerate",
        "/api/v1/resummarize",
        "/api/v1/retry-summary",
    )

    for endpoint in forbidden:
        assert endpoint not in js


def test_m7_4_has_no_backend_result_export_endpoint():
    js = read_app_js().lower()

    forbidden = (
        "/api/v1/export",
        "/api/v1/download",
        "/api/v1/results/download",
    )

    for endpoint in forbidden:
        assert endpoint not in js
