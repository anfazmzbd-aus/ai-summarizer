"""V13 M7.7 canonical architecture and compatibility certification.

This suite certifies that V13 productization remains additive around
the production-certified V12 architecture.

Canonical execution path:

    HTTP / supported frontend
        -> /api/v1/summarize
        -> SummarizationApplication
        -> bounded intelligence
        -> existing V9 summarization pipeline
        -> AI runtime/provider
        -> product-safe response

V13 additions must not introduce:

* a second summarization endpoint
* direct frontend/provider execution
* file-upload summarization bypass
* client-side private model mapping
* separate regeneration execution
* persistence as part of the MVP workflow
* replacement V9/V10/V11 execution architecture

Compatibility requirements:

* the legacy text/provider/model summarize request remains valid
* legacy provider/model values remain authoritative when product_model
  is omitted
* product_model is additive
* approved product_model resolves server-side
* summary controls are additive
* historical response fields remain available
* V13 metadata additions remain optional/additive
* TXT/PDF extraction rejoins the same summarize path
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.schemas import (
    SummarizeRequest,
)
from app.core.product_model_catalogue import (
    ProductModel,
    ProductModelCatalogue,
)
from app.core.product_options import (
    SummaryLength,
    SummaryType,
)
from app.main import app
from app.routes import ai as ai_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

AI_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "ai.py"

APPLICATION_PATH = PROJECT_ROOT / "app" / "api" / "application.py"

APPLICATION_CONTRACTS_PATH = PROJECT_ROOT / "app" / "core" / "application_contracts.py"

APPLICATION_METADATA_PATH = PROJECT_ROOT / "app" / "core" / "application_metadata.py"

PIPELINE_ADAPTER_PATH = (
    PROJECT_ROOT / "app" / "core" / "summarization_pipeline_adapter.py"
)

PIPELINE_FACTORY_PATH = (
    PROJECT_ROOT / "app" / "core" / "summarization_pipeline_factory.py"
)

INTELLIGENCE_INTEGRATION_PATH = (
    PROJECT_ROOT / "app" / "core" / "intelligence_integration.py"
)

DEPENDENCIES_PATH = PROJECT_ROOT / "app" / "api" / "dependencies.py"

FILE_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "file_extraction.py"

FILE_EXTRACTION_PATH = PROJECT_ROOT / "app" / "core" / "file_extraction.py"

PRODUCT_CONFIG_ROUTE_PATH = PROJECT_ROOT / "app" / "routes" / "product_config.py"

PRODUCT_MODEL_CATALOGUE_PATH = (
    PROJECT_ROOT / "app" / "core" / "product_model_catalogue.py"
)


client = TestClient(app)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse(path: Path) -> ast.Module:
    return ast.parse(read(path))


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
    trace_id = "m7-7-trace"
    explainability_summary = "canonical compatibility"
    attributes = {
        "intelligence_observability_status": "normal",
    }


class FakeResult:
    def __init__(
        self,
        *,
        model: str,
        summary: str = "canonical compatibility summary",
    ) -> None:
        self.summary = summary
        self.model = model
        self.prompt_tokens = 12
        self.completion_tokens = 8
        self.metadata = FakeMetadata()

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class CapturingApplication:
    def __init__(
        self,
        captured: dict,
    ) -> None:
        self._captured = captured

    async def summarize(
        self,
        request,
    ):
        self._captured["request"] = request

        return FakeResult(
            model=request.model or "",
        )


def install_application(
    monkeypatch,
    captured: dict,
) -> None:
    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: CapturingApplication(captured),
    )


# ---------------------------------------------------------------------------
# Frozen canonical component inventory
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    (
        APPLICATION_PATH,
        APPLICATION_CONTRACTS_PATH,
        APPLICATION_METADATA_PATH,
        PIPELINE_ADAPTER_PATH,
        PIPELINE_FACTORY_PATH,
        INTELLIGENCE_INTEGRATION_PATH,
        DEPENDENCIES_PATH,
        AI_ROUTE_PATH,
    ),
)
def test_canonical_component_exists(
    path,
):
    assert path.is_file()


def test_canonical_application_class_remains_present():
    source = read(APPLICATION_PATH)

    assert "class SummarizationApplication" in source


def test_application_request_contract_remains_present():
    source = read(APPLICATION_CONTRACTS_PATH)

    assert "class SummarizationApplicationRequest" in source


def test_application_result_contract_remains_present():
    source = read(APPLICATION_CONTRACTS_PATH)

    assert "class SummarizationApplicationResult" in source


def test_application_metadata_contract_remains_present():
    source = read(APPLICATION_METADATA_PATH)

    assert "class SummarizationExecutionMetadata" in source


# ---------------------------------------------------------------------------
# Canonical application -> intelligence -> V9 pipeline
# ---------------------------------------------------------------------------


def test_application_owns_intelligence_boundary():
    source = read(APPLICATION_PATH)

    assert "ApplicationIntelligenceBoundary" in source


def test_application_evaluates_intelligence_before_pipeline():
    source = read(APPLICATION_PATH)

    intelligence_position = source.index("self._intelligence.evaluate(")

    pipeline_position = source.index("self._pipeline.run(")

    assert intelligence_position < pipeline_position


def test_application_preserves_review_boundary():
    source = read(APPLICATION_PATH)

    assert "ApplicationReviewRequiredError" in source

    assert 'intelligence_result.mode == "review"' in source


def test_application_uses_async_pipeline_adapter():
    source = read(APPLICATION_PATH)

    assert "AsyncSummarizationPipelineAdapter" in source


def test_application_executes_pipeline():
    source = read(APPLICATION_PATH)

    assert "self._pipeline.run(" in source


def test_application_passes_source_to_pipeline():
    source = read(APPLICATION_PATH)

    assert "request.text" in source


def test_application_passes_summary_intent_to_pipeline():
    source = read(APPLICATION_PATH)

    assert "intent=summary_profile.intent" in source


# ---------------------------------------------------------------------------
# Existing V9 pipeline remains authoritative
# ---------------------------------------------------------------------------


def test_pipeline_adapter_identifies_existing_v9_pipeline():
    source = read(PIPELINE_ADAPTER_PATH)

    assert "existing V9 summarization pipeline" in source


def test_pipeline_adapter_imports_summarization_pipeline():
    source = read(PIPELINE_ADAPTER_PATH)

    assert "SummarizationPipeline" in source


def test_pipeline_adapter_wraps_pipeline_instance():
    source = read(PIPELINE_ADAPTER_PATH)

    assert "self._pipeline = pipeline" in source


def test_pipeline_adapter_delegates_to_pipeline_run():
    source = read(PIPELINE_ADAPTER_PATH)

    assert "self._pipeline.run" in source


def test_pipeline_adapter_preserves_async_boundary():
    source = read(PIPELINE_ADAPTER_PATH)

    assert "asyncio.to_thread" in source

    assert "asyncio.run_coroutine_threadsafe" in source


def test_pipeline_factory_uses_existing_pipeline():
    source = read(PIPELINE_FACTORY_PATH)

    assert "SummarizationPipeline(" in source


def test_pipeline_factory_uses_existing_chunker():
    source = read(PIPELINE_FACTORY_PATH)

    assert "TextChunker()" in source


def test_pipeline_factory_returns_async_adapter():
    source = read(PIPELINE_FACTORY_PATH)

    assert "AsyncSummarizationPipelineAdapter(" in source


# ---------------------------------------------------------------------------
# Single public summarization endpoint
# ---------------------------------------------------------------------------


def test_api_registers_canonical_summarize_endpoint():
    paths = [
        route.path
        for route in app.routes
        if hasattr(
            route,
            "path",
        )
    ]

    assert "/api/v1/summarize" in paths


def test_api_has_exactly_one_registered_summarize_path():
    paths = [
        route.path
        for route in app.routes
        if hasattr(
            route,
            "path",
        )
    ]

    assert paths.count("/api/v1/summarize") == 1


def test_frontend_has_exactly_one_summarize_fetch():
    js = read(APP_JS_PATH)

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_frontend_has_no_direct_alternate_summary_endpoint():
    js = read(APP_JS_PATH).lower()

    forbidden = (
        "/api/v1/resummarize",
        "/api/v1/regenerate",
        "/api/v1/retry-summary",
        "/api/v1/executive-summary",
        "/api/v1/key-points",
        "/api/v1/action-items",
        "/api/v1/findings",
        "/api/v1/insights",
        "/api/v1/technical-summary",
    )

    for endpoint in forbidden:
        assert endpoint not in js


# ---------------------------------------------------------------------------
# HTTP route retains canonical application boundary
# ---------------------------------------------------------------------------


def test_ai_route_builds_canonical_application():
    source = read(AI_ROUTE_PATH)

    assert "build_summarization_application()" in source


def test_ai_route_constructs_application_request():
    source = read(AI_ROUTE_PATH)

    assert "SummarizationApplicationRequest(" in source


def test_ai_route_calls_application_summarize():
    source = read(AI_ROUTE_PATH)

    assert "application.summarize(" in source


def test_ai_route_does_not_directly_construct_v9_pipeline():
    source = read(AI_ROUTE_PATH)

    assert "SummarizationPipeline(" not in source


def test_ai_route_does_not_directly_construct_provider_client():
    source = read(AI_ROUTE_PATH)

    forbidden = (
        "AsyncOpenAI(",
        "OpenAIProvider(",
        "LLMClient(",
    )

    for value in forbidden:
        assert value not in source


# ---------------------------------------------------------------------------
# Frontend cannot bypass canonical application
# ---------------------------------------------------------------------------


def test_frontend_does_not_reference_openai_sdk():
    js = read(APP_JS_PATH).lower()

    assert "asyncopenai" not in js


def test_frontend_does_not_reference_provider_credentials():
    js = read(APP_JS_PATH).lower()

    forbidden = (
        "openai_api_key",
        "openai_base_url",
        "authorization: bearer",
        "api_key",
    )

    for value in forbidden:
        assert value not in js


def test_frontend_does_not_map_public_model_to_provider():
    js = read(APP_JS_PATH)

    assert "model.provider" not in js

    assert "model.runtime_model" not in js


def test_frontend_sends_public_product_model_id_only():
    js = read(APP_JS_PATH)

    assert "product_model: modelSelection.value" in js


# ---------------------------------------------------------------------------
# Legacy V12 request compatibility
# ---------------------------------------------------------------------------


def test_legacy_request_schema_still_has_text():
    fields = SummarizeRequest.model_fields

    assert "text" in fields


def test_legacy_request_schema_still_has_provider():
    fields = SummarizeRequest.model_fields

    assert "provider" in fields


def test_legacy_request_schema_still_has_model():
    fields = SummarizeRequest.model_fields

    assert "model" in fields


def test_legacy_provider_default_is_fake():
    field = SummarizeRequest.model_fields["provider"]

    assert field.default == "fake"


def test_legacy_model_default_is_demo():
    field = SummarizeRequest.model_fields["model"]

    assert field.default == "demo"


def test_minimal_legacy_request_remains_valid():
    request = SummarizeRequest(text="Legacy compatibility source.")

    assert request.text == "Legacy compatibility source."

    assert request.provider == "fake"

    assert request.model == "demo"


def test_legacy_request_defaults_to_general_summary():
    request = SummarizeRequest(text="Legacy compatibility source.")

    assert request.summary_type == SummaryType.GENERAL


def test_legacy_request_defaults_to_medium_length():
    request = SummarizeRequest(text="Legacy compatibility source.")

    assert request.summary_length == SummaryLength.MEDIUM


def test_legacy_request_defaults_to_no_instructions():
    request = SummarizeRequest(text="Legacy compatibility source.")

    assert request.instructions is None


def test_product_model_is_additive_request_field():
    fields = SummarizeRequest.model_fields

    assert "product_model" in fields


def test_product_model_defaults_to_none():
    request = SummarizeRequest(text="Legacy compatibility source.")

    assert request.product_model is None


# ---------------------------------------------------------------------------
# Legacy API execution compatibility
# ---------------------------------------------------------------------------


def test_legacy_request_reaches_canonical_application(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200
    assert "request" in captured


def test_legacy_provider_reaches_application_unchanged(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "legacy-provider",
            "model": "legacy-model",
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.provider == "legacy-provider"


def test_legacy_model_reaches_application_unchanged(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "legacy-provider",
            "model": "legacy-model",
        },
    )

    assert response.status_code == 200

    assert captured["request"].model == "legacy-model"


def test_legacy_request_does_not_require_product_catalogue(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    def catalogue_must_not_run():
        raise AssertionError("legacy request must not " "require product catalogue")

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        catalogue_must_not_run,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200


def test_legacy_response_retains_summary(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "fake",
            "model": "demo",
        },
    )

    payload = response.json()

    assert payload["summary"] == "canonical compatibility summary"


def test_legacy_response_retains_model(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.json()["model"] == "demo"


def test_legacy_response_retains_prompt_tokens(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.json()["prompt_tokens"] == 12


def test_legacy_response_retains_completion_tokens(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.json()["completion_tokens"] == 8


def test_legacy_response_retains_total_tokens(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.json()["total_tokens"] == 20


def test_v13_metadata_is_additive_to_legacy_response(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy source",
            "provider": "fake",
            "model": "demo",
        },
    )

    payload = response.json()

    assert "metadata" in payload

    assert payload["metadata"]["strategy"] == "direct"


# ---------------------------------------------------------------------------
# Product-model path remains additive
# ---------------------------------------------------------------------------


def test_product_model_request_resolves_server_side(
    monkeypatch,
):
    captured = {}
    catalogue = build_catalogue()

    install_application(
        monkeypatch,
        captured,
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Product source",
            "provider": "untrusted-provider",
            "model": "untrusted-model",
            "product_model": "quality",
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.provider == "fake"

    assert request.model == "runtime-quality"


def test_product_model_overrides_public_provider_value(
    monkeypatch,
):
    captured = {}
    catalogue = build_catalogue()

    install_application(
        monkeypatch,
        captured,
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Product source",
            "provider": "client-provider",
            "model": "client-model",
            "product_model": "balanced",
        },
    )

    assert response.status_code == 200

    assert captured["request"].provider == "fake"


def test_product_model_overrides_public_model_value(
    monkeypatch,
):
    captured = {}
    catalogue = build_catalogue()

    install_application(
        monkeypatch,
        captured,
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Product source",
            "provider": "client-provider",
            "model": "client-model",
            "product_model": "balanced",
        },
    )

    assert response.status_code == 200

    assert captured["request"].model == "runtime-balanced"


def test_product_model_path_preserves_summary_type(
    monkeypatch,
):
    captured = {}
    catalogue = build_catalogue()

    install_application(
        monkeypatch,
        captured,
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Product source",
            "product_model": "quality",
            "summary_type": "technical",
            "summary_length": "detailed",
        },
    )

    assert response.status_code == 200

    assert captured["request"].summary_type == SummaryType.TECHNICAL


def test_product_model_path_preserves_summary_length(
    monkeypatch,
):
    captured = {}
    catalogue = build_catalogue()

    install_application(
        monkeypatch,
        captured,
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Product source",
            "product_model": "quality",
            "summary_type": "technical",
            "summary_length": "detailed",
        },
    )

    assert response.status_code == 200

    assert captured["request"].summary_length == SummaryLength.DETAILED


def test_product_model_path_preserves_custom_instructions(
    monkeypatch,
):
    captured = {}
    catalogue = build_catalogue()

    install_application(
        monkeypatch,
        captured,
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Product source",
            "product_model": "quality",
            "summary_type": "executive",
            "summary_length": "medium",
            "instructions": ("Focus on architecture risk."),
        },
    )

    assert response.status_code == 200

    assert captured["request"].instructions == "Focus on architecture risk."


def test_unknown_product_model_fails_before_application(
    monkeypatch,
):
    catalogue = build_catalogue()
    application_called = False

    class MustNotRun:
        async def summarize(
            self,
            request,
        ):
            nonlocal application_called

            application_called = True

            raise AssertionError("canonical application " "must not execute")

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        MustNotRun,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Product source",
            "product_model": "unknown",
        },
    )

    assert response.status_code == 422

    assert application_called is False


# ---------------------------------------------------------------------------
# Product configuration remains presentation-safe
# ---------------------------------------------------------------------------


def test_product_config_endpoint_remains_registered():
    paths = {
        route.path
        for route in app.routes
        if hasattr(
            route,
            "path",
        )
    }

    assert "/api/v1/product-config" in paths


def test_product_config_route_uses_catalogue():
    source = read(PRODUCT_CONFIG_ROUTE_PATH)

    assert "build_product_model_catalogue" in source


def test_product_model_catalogue_keeps_private_provider_mapping():
    source = read(PRODUCT_MODEL_CATALOGUE_PATH)

    assert "provider: str" in source

    assert "model: str" in source


def test_frontend_public_config_does_not_use_private_mapping():
    js = read(APP_JS_PATH)

    forbidden = (
        "model.provider",
        "model.runtime_model",
        "model.api_key",
        "model.base_url",
    )

    for value in forbidden:
        assert value not in js


# ---------------------------------------------------------------------------
# File extraction remains preprocessing only
# ---------------------------------------------------------------------------


def test_file_extraction_endpoint_remains_registered():
    paths = {
        route.path
        for route in app.routes
        if hasattr(
            route,
            "path",
        )
    }

    assert "/api/v1/files/extract" in paths


def test_file_route_does_not_import_canonical_application():
    tree = parse(FILE_ROUTE_PATH)

    imported = set()

    for node in ast.walk(tree):
        if (
            isinstance(
                node,
                ast.ImportFrom,
            )
            and node.module
        ):
            imported.add(node.module)

        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imported.add(alias.name)

    assert "app.api.application" not in imported


def test_file_extraction_service_does_not_import_application():
    tree = parse(FILE_EXTRACTION_PATH)

    imported = set()

    for node in ast.walk(tree):
        if (
            isinstance(
                node,
                ast.ImportFrom,
            )
            and node.module
        ):
            imported.add(node.module)

        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imported.add(alias.name)

    assert "app.api.application" not in imported


def test_file_extraction_route_does_not_call_summarize_endpoint():
    source = read(FILE_ROUTE_PATH)

    assert "/api/v1/summarize" not in source


def test_file_extraction_service_does_not_call_summarization():
    source = read(FILE_EXTRACTION_PATH)

    assert "SummarizationApplication" not in source

    assert "build_summarization_application" not in source


def test_frontend_file_extraction_returns_text_to_main_input():
    js = read(APP_JS_PATH)

    assert "inputText.value = payload.text;" in js


def test_frontend_extraction_does_not_auto_submit_summary():
    js = read(APP_JS_PATH)

    start = js.index("async function extractFile(")

    end = js.index(
        "function handleSelectedFiles(",
        start,
    )

    extraction = js[start:end]

    assert "summaryForm.requestSubmit()" not in extraction

    assert "/api/v1/summarize" not in extraction


# ---------------------------------------------------------------------------
# Regeneration remains canonical
# ---------------------------------------------------------------------------


def test_regenerate_reuses_summary_form():
    js = read(APP_JS_PATH)

    start = js.index("function regenerateSummary()")

    end = js.index(
        "regenerateSummaryButton.addEventListener",
        start,
    )

    block = js[start:end]

    assert "summaryForm.requestSubmit();" in block


def test_regenerate_has_no_direct_network_call():
    js = read(APP_JS_PATH)

    start = js.index("function regenerateSummary()")

    end = js.index(
        "regenerateSummaryButton.addEventListener",
        start,
    )

    block = js[start:end]

    assert "fetch(" not in block


def test_regenerate_has_no_provider_logic():
    js = read(APP_JS_PATH)

    start = js.index("function regenerateSummary()")

    end = js.index(
        "regenerateSummaryButton.addEventListener",
        start,
    )

    block = js[start:end].lower()

    forbidden = (
        "provider",
        "api_key",
        "base_url",
        "runtime_model",
    )

    for value in forbidden:
        assert value not in block


# ---------------------------------------------------------------------------
# Result export remains client-side
# ---------------------------------------------------------------------------


def test_download_remains_browser_side():
    js = read(APP_JS_PATH)

    start = js.index("function downloadSummary()")

    end = js.index(
        "downloadSummaryButton.addEventListener",
        start,
    )

    block = js[start:end]

    assert "new Blob(" in block

    assert "URL.createObjectURL" in block


def test_download_has_no_backend_request():
    js = read(APP_JS_PATH)

    start = js.index("function downloadSummary()")

    end = js.index(
        "downloadSummaryButton.addEventListener",
        start,
    )

    block = js[start:end]

    assert "fetch(" not in block


# ---------------------------------------------------------------------------
# No MVP persistence architecture added
# ---------------------------------------------------------------------------


def test_frontend_has_no_local_storage_dependency():
    js = read(APP_JS_PATH).lower()

    assert "localstorage" not in js


def test_frontend_has_no_session_storage_dependency():
    js = read(APP_JS_PATH).lower()

    assert "sessionstorage" not in js


def test_frontend_has_no_indexeddb_dependency():
    js = read(APP_JS_PATH).lower()

    assert "indexeddb" not in js


def test_frontend_has_no_history_endpoint():
    js = read(APP_JS_PATH).lower()

    forbidden = (
        "/api/v1/history",
        "/api/v1/summaries/history",
        "/api/v1/results/history",
    )

    for endpoint in forbidden:
        assert endpoint not in js


# ---------------------------------------------------------------------------
# Product controls remain additive
# ---------------------------------------------------------------------------


def test_summary_type_control_remains_present():
    html = read(INDEX_HTML_PATH)

    assert 'id="summaryType"' in html


def test_summary_length_control_remains_present():
    html = read(INDEX_HTML_PATH)

    assert 'id="summaryLength"' in html


def test_custom_instructions_control_remains_present():
    html = read(INDEX_HTML_PATH)

    assert 'id="customInstructions"' in html


def test_model_selection_control_remains_present():
    html = read(INDEX_HTML_PATH)

    assert 'id="modelSelection"' in html


def test_frontend_submits_all_controls_through_same_request():
    js = read(APP_JS_PATH)

    assert "text: normalizedText" in js

    assert "summary_type: summaryType.value" in js

    assert "summary_length: summaryLength.value" in js

    assert "customInstructions.value.trim() || null" in js

    assert "product_model: modelSelection.value" in js


# ---------------------------------------------------------------------------
# Response compatibility and safe metadata
# ---------------------------------------------------------------------------


def test_response_metadata_remains_product_safe(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Compatibility source.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    metadata = response.json()["metadata"]

    assert metadata["strategy"] == "direct"

    assert metadata["chunk_count"] == 1

    assert metadata["intelligence_mode"] == "preserve"


def test_response_does_not_expose_provider_credentials(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Compatibility source.",
            "provider": "fake",
            "model": "demo",
        },
    )

    serialized = response.text.lower()

    forbidden = (
        "api_key",
        "authorization",
        "base_url",
    )

    for value in forbidden:
        assert value not in serialized


# ---------------------------------------------------------------------------
# Architecture import boundaries
# ---------------------------------------------------------------------------


def test_frontend_is_not_referenced_by_application_boundary():
    source = read(APPLICATION_PATH).lower()

    assert "static/app.js" not in source

    assert "templates/index.html" not in source


def test_pipeline_adapter_has_no_frontend_dependency():
    source = read(PIPELINE_ADAPTER_PATH).lower()

    forbidden = (
        "fastapi",
        "templates",
        "static",
        "javascript",
    )

    for value in forbidden:
        assert value not in source


def test_pipeline_factory_has_no_frontend_dependency():
    source = read(PIPELINE_FACTORY_PATH).lower()

    forbidden = (
        "fastapi",
        "templates",
        "static",
        "javascript",
    )

    for value in forbidden:
        assert value not in source


def test_product_model_catalogue_has_no_frontend_dependency():
    source = read(PRODUCT_MODEL_CATALOGUE_PATH).lower()

    forbidden = (
        "document.",
        "window.",
        "localstorage",
    )

    for value in forbidden:
        assert value not in source


# ---------------------------------------------------------------------------
# Route-level compatibility
# ---------------------------------------------------------------------------


def test_summarize_method_remains_post():
    matching = [
        route
        for route in app.routes
        if getattr(
            route,
            "path",
            None,
        )
        == "/api/v1/summarize"
    ]

    assert len(matching) == 1

    assert "POST" in matching[0].methods


def test_product_config_method_remains_get():
    matching = [
        route
        for route in app.routes
        if getattr(
            route,
            "path",
            None,
        )
        == "/api/v1/product-config"
    ]

    assert len(matching) == 1

    assert "GET" in matching[0].methods


def test_file_extraction_method_remains_post():
    matching = [
        route
        for route in app.routes
        if getattr(
            route,
            "path",
            None,
        )
        == "/api/v1/files/extract"
    ]

    assert len(matching) == 1

    assert "POST" in matching[0].methods


# ---------------------------------------------------------------------------
# M7.7 final architecture invariants
# ---------------------------------------------------------------------------


def test_m7_7_single_browser_summarization_path():
    js = read(APP_JS_PATH)

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_m7_7_single_registered_summarization_route():
    routes = [
        route
        for route in app.routes
        if getattr(
            route,
            "path",
            None,
        )
        == "/api/v1/summarize"
    ]

    assert len(routes) == 1


def test_m7_7_route_targets_canonical_application():
    source = read(AI_ROUTE_PATH)

    assert "build_summarization_application()" in source

    assert "application.summarize(" in source


def test_m7_7_application_targets_existing_pipeline_adapter():
    source = read(APPLICATION_PATH)

    assert "AsyncSummarizationPipelineAdapter" in source

    assert "self._pipeline.run(" in source


def test_m7_7_adapter_targets_existing_v9_pipeline():
    source = read(PIPELINE_ADAPTER_PATH)

    assert "SummarizationPipeline" in source

    assert "self._pipeline.run" in source


def test_m7_7_file_ingestion_is_preprocessing_only():
    route = read(FILE_ROUTE_PATH)

    service = read(FILE_EXTRACTION_PATH)

    combined = route + "\n" + service

    forbidden = (
        "build_summarization_application",
        "SummarizationApplication(",
        "/api/v1/summarize",
    )

    for value in forbidden:
        assert value not in combined


def test_m7_7_regeneration_reuses_canonical_submit():
    js = read(APP_JS_PATH)

    start = js.index("function regenerateSummary()")

    end = js.index(
        "regenerateSummaryButton.addEventListener",
        start,
    )

    block = js[start:end]

    assert "summaryForm.requestSubmit();" in block

    assert "fetch(" not in block


def test_m7_7_product_model_resolution_is_server_side():
    route = read(AI_ROUTE_PATH)

    js = read(APP_JS_PATH)

    assert "build_product_model_catalogue" in route

    assert "catalogue.resolve(" in route

    assert "model.provider" not in js

    assert "model.runtime_model" not in js


def test_m7_7_legacy_request_remains_supported(
    monkeypatch,
):
    captured = {}

    install_application(
        monkeypatch,
        captured,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": ("Legacy V12-compatible " "summarization request."),
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.provider == "fake"
    assert request.model == "demo"

    assert request.summary_type == SummaryType.GENERAL

    assert request.summary_length == SummaryLength.MEDIUM

    assert request.instructions is None


def test_m7_7_product_features_are_additive(
    monkeypatch,
):
    captured = {}
    catalogue = build_catalogue()

    install_application(
        monkeypatch,
        captured,
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": ("V13 additive product request."),
            "product_model": "quality",
            "summary_type": "executive",
            "summary_length": "detailed",
            "instructions": ("Focus on compatibility."),
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.provider == "fake"

    assert request.model == "runtime-quality"

    assert request.summary_type == SummaryType.EXECUTIVE

    assert request.summary_length == SummaryLength.DETAILED

    assert request.instructions == "Focus on compatibility."


def test_m7_7_no_alternate_execution_architecture():
    frontend = read(APP_JS_PATH).lower()

    file_route = read(FILE_ROUTE_PATH)

    file_service = read(FILE_EXTRACTION_PATH)

    assert frontend.count('fetch("/api/v1/summarize"') == 1

    assert "build_summarization_application" not in file_route

    assert "build_summarization_application" not in file_service


def test_m7_7_remains_deterministic_and_offline():
    tree = parse(Path(__file__))

    modules = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                modules.add(
                    alias.name.split(
                        ".",
                        1,
                    )[0]
                )

        if (
            isinstance(
                node,
                ast.ImportFrom,
            )
            and node.module
        ):
            modules.add(
                node.module.split(
                    ".",
                    1,
                )[0]
            )

    forbidden = {
        "requests",
        "httpx",
        "openai",
    }

    assert modules.isdisjoint(forbidden)
