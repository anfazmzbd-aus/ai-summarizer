"""V13 M4.6 model configuration and failure hardening tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config.ai_settings import AISettings
from app.core.product_model_catalogue import (
    ProductModel,
    ProductModelCatalogue,
    build_product_model_catalogue,
)
from app.main import app
from app.routes import ai as ai_route
from app.routes import product_config as product_config_route


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "static" / "app.js"

client = TestClient(app)


def read_script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def make_settings(
    *,
    provider: str = "fake",
    api_key: str = "",
    model: str = "gpt-5-mini",
    base_url: str | None = None,
    organization: str | None = None,
) -> AISettings:
    return AISettings(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
        organization=organization,
    )


def test_missing_product_models_configuration_uses_safe_default(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "AI_PRODUCT_MODELS",
        raising=False,
    )

    catalogue = build_product_model_catalogue(make_settings(provider="fake"))

    assert len(catalogue.models) == 1

    model = catalogue.default

    assert model.id == "default"
    assert model.label == "Default"
    assert model.provider == "fake"
    assert model.model == "demo"
    assert model.is_default is True


def test_blank_product_models_configuration_uses_safe_default(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "   ",
    )

    catalogue = build_product_model_catalogue(make_settings(provider="fake"))

    assert catalogue.default.id == "default"
    assert catalogue.default.provider == "fake"
    assert catalogue.default.model == "demo"


def test_configured_first_model_is_default(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        ("balanced|Balanced|runtime-balanced;" "quality|Quality|runtime-quality"),
    )

    catalogue = build_product_model_catalogue(make_settings(provider="fake"))

    assert catalogue.default.id == "balanced"
    assert catalogue.default.model == "runtime-balanced"

    assert catalogue.models[1].id == "quality"
    assert catalogue.models[1].is_default is False


def test_openai_default_uses_server_runtime_model(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "AI_PRODUCT_MODELS",
        raising=False,
    )

    catalogue = build_product_model_catalogue(
        make_settings(
            provider="openai",
            api_key="private-key",
            model="approved-runtime-model",
        )
    )

    assert catalogue.default.id == "default"
    assert catalogue.default.provider == "openai"
    assert catalogue.default.model == "approved-runtime-model"


def test_unsupported_provider_configuration_is_rejected(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "AI_PRODUCT_MODELS",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="unsupported AI provider",
    ):
        build_product_model_catalogue(
            make_settings(
                provider="unsupported-provider",
            )
        )


@pytest.mark.parametrize(
    "configured_value",
    [
        ";",
        "default|Default",
        "default||runtime-model",
        "|Default|runtime-model",
        "default|Default|",
        "default|Default|runtime;",
    ],
)
def test_malformed_catalogue_configuration_is_rejected(
    monkeypatch,
    configured_value: str,
) -> None:
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        configured_value,
    )

    with pytest.raises(ValueError):
        build_product_model_catalogue(make_settings(provider="fake"))


def test_duplicate_product_ids_are_rejected(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        ("default|Default|runtime-one;" "default|Duplicate|runtime-two"),
    )

    with pytest.raises(
        ValueError,
        match="product model ids must be unique",
    ):
        build_product_model_catalogue(make_settings(provider="fake"))


def test_unknown_product_model_is_rejected_by_catalogue() -> None:
    catalogue = ProductModelCatalogue(
        (
            ProductModel(
                id="default",
                label="Default",
                provider="fake",
                model="demo",
                is_default=True,
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="unsupported product model",
    ):
        catalogue.resolve("not-approved")


def test_product_config_exposes_only_public_model_fields(
    monkeypatch,
) -> None:
    catalogue = ProductModelCatalogue(
        (
            ProductModel(
                id="quality",
                label="Quality",
                provider="openai",
                model="private-runtime-model",
                is_default=True,
            ),
        )
    )

    monkeypatch.setattr(
        product_config_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.get("/api/v1/product-config")

    assert response.status_code == 200

    payload = response.json()

    assert payload == {
        "models": [
            {
                "id": "quality",
                "label": "Quality",
                "is_default": True,
            }
        ]
    }


def test_product_config_does_not_expose_runtime_model(
    monkeypatch,
) -> None:
    catalogue = ProductModelCatalogue(
        (
            ProductModel(
                id="quality",
                label="Quality",
                provider="openai",
                model="private-runtime-model",
                is_default=True,
            ),
        )
    )

    monkeypatch.setattr(
        product_config_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.get("/api/v1/product-config")

    serialized = response.text

    assert "private-runtime-model" not in serialized
    assert '"provider"' not in serialized


def test_product_config_does_not_expose_credentials(
    monkeypatch,
) -> None:
    private_values = (
        "private-api-key",
        "https://private.example.test/v1",
        "private-organization",
    )

    catalogue = ProductModelCatalogue(
        (
            ProductModel(
                id="default",
                label="Default",
                provider="openai",
                model="runtime-model",
                is_default=True,
            ),
        )
    )

    monkeypatch.setattr(
        product_config_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.get("/api/v1/product-config")

    serialized = response.text

    for private_value in private_values:
        assert private_value not in serialized


def test_product_config_schema_has_no_private_runtime_fields() -> None:
    from app.api.product_config_schemas import (
        ProductModelOption,
    )

    fields = set(ProductModelOption.model_fields)

    assert fields == {
        "id",
        "label",
        "is_default",
    }


def test_frontend_enters_loading_state_before_configuration_request() -> None:
    script = read_script()

    loading_position = script.index("MODEL_STATE.LOADING")

    product_config_position = script.index('"/api/v1/product-config"')

    assert loading_position < product_config_position


def test_frontend_disables_model_selection_while_loading() -> None:
    script = read_script()

    assert "if (nextState === MODEL_STATE.LOADING)" in script
    assert "modelSelection.disabled = true;" in script


def test_frontend_disables_model_selection_on_configuration_error() -> None:
    script = read_script()

    error_state_start = script.index("if (nextState === MODEL_STATE.ERROR)")

    error_state_fragment = script[error_state_start : error_state_start + 500]

    assert "modelSelection.disabled = true;" in error_state_fragment


def test_frontend_requires_ready_model_before_submission() -> None:
    script = read_script()

    assert "currentModelState === MODEL_STATE.READY" in script

    assert "!hasAvailableModel()" in script


def test_frontend_submission_is_disabled_without_available_model() -> None:
    script = read_script()

    assert "!hasAvailableModel();" in script


def test_frontend_validates_product_config_is_array() -> None:
    script = read_script()

    assert "!Array.isArray(models)" in script


def test_frontend_rejects_empty_product_model_list() -> None:
    script = read_script()

    assert "models.length === 0" in script


def test_frontend_validates_public_model_id() -> None:
    script = read_script()

    assert 'typeof model.id === "string"' in script
    assert "model.id.trim().length > 0" in script


def test_frontend_validates_public_model_label() -> None:
    script = read_script()

    assert 'typeof model.label === "string"' in script
    assert "model.label.trim().length > 0" in script


def test_frontend_validates_default_flag() -> None:
    script = read_script()

    assert 'typeof model.is_default === "boolean"' in script


def test_frontend_requires_exactly_one_default_model() -> None:
    script = read_script()

    assert "defaults.length === 1" in script


def test_frontend_uses_safe_configuration_error_message() -> None:
    script = read_script()

    assert '"Model options are unavailable."' in script


def test_frontend_does_not_render_runtime_provider_metadata() -> None:
    script = read_script()

    assert "model.provider" not in script
    assert "model.runtime_model" not in script
    assert "model.api_key" not in script
    assert "model.base_url" not in script
    assert "model.organization" not in script


def test_frontend_model_option_uses_only_public_identity() -> None:
    script = read_script()

    assert "option.value = model.id;" in script
    assert "option.textContent = model.label;" in script


def test_frontend_sends_only_selected_product_model_id() -> None:
    script = read_script()

    assert "product_model: modelSelection.value" in script

    assert "product_model: modelSelection.label" not in script
    assert "product_model: model.label" not in script


def test_unknown_product_model_returns_safe_authorization_error(
    monkeypatch,
) -> None:
    catalogue = ProductModelCatalogue(
        (
            ProductModel(
                id="default",
                label="Default",
                provider="fake",
                model="private-runtime-model",
                is_default=True,
            ),
        )
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Example source",
            "product_model": "not-approved",
        },
    )

    assert response.status_code == 422

    payload = response.json()

    assert payload["detail"]["error"]["code"] == ("INVALID_APPLICATION_STATE")
    assert payload["detail"]["error"]["message"] == (
        "summarization could not be authorized"
    )


def test_unknown_product_model_error_does_not_leak_runtime_mapping(
    monkeypatch,
) -> None:
    catalogue = ProductModelCatalogue(
        (
            ProductModel(
                id="default",
                label="Default",
                provider="fake",
                model="private-runtime-model",
                is_default=True,
            ),
        )
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Example source",
            "product_model": "not-approved",
        },
    )

    serialized = response.text

    assert "private-runtime-model" not in serialized
    assert "unsupported product model" not in serialized


def test_product_model_path_ignores_untrusted_provider_and_model(
    monkeypatch,
) -> None:
    captured_request = {}

    class FakeResult:
        summary = "approved summary"
        model = "approved-runtime-model"
        prompt_tokens = 10
        completion_tokens = 5

        @property
        def total_tokens(self) -> int:
            return self.prompt_tokens + self.completion_tokens

        class Metadata:
            strategy = "direct"
            chunk_count = 1
            intelligence_mode = "preserve"
            trace_id = "trace"
            explainability_summary = "preserved"
            attributes = {}

        metadata = Metadata()

    class FakeApplication:
        async def summarize(self, request):
            captured_request["request"] = request
            return FakeResult()

    catalogue = ProductModelCatalogue(
        (
            ProductModel(
                id="approved",
                label="Approved",
                provider="fake",
                model="approved-runtime-model",
                is_default=True,
            ),
        )
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
            "text": "Example source",
            "provider": "attacker-provider",
            "model": "attacker-model",
            "product_model": "approved",
        },
    )

    assert response.status_code == 200

    request = captured_request["request"]

    assert request.provider == "fake"
    assert request.model == "approved-runtime-model"


def test_product_model_path_does_not_execute_for_unknown_id(
    monkeypatch,
) -> None:
    application_called = False

    class FakeApplication:
        async def summarize(self, request):
            nonlocal application_called
            application_called = True
            raise AssertionError("application must not execute")

    catalogue = ProductModelCatalogue(
        (
            ProductModel(
                id="default",
                label="Default",
                provider="fake",
                model="demo",
                is_default=True,
            ),
        )
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
            "text": "Example source",
            "product_model": "unknown",
        },
    )

    assert response.status_code == 422
    assert application_called is False


def test_legacy_request_remains_independent_of_product_catalogue(
    monkeypatch,
) -> None:
    captured_request = {}

    class FakeResult:
        summary = "legacy summary"
        model = "demo"
        prompt_tokens = 10
        completion_tokens = 5

        @property
        def total_tokens(self) -> int:
            return self.prompt_tokens + self.completion_tokens

        class Metadata:
            strategy = "direct"
            chunk_count = 1
            intelligence_mode = "preserve"
            trace_id = "trace"
            explainability_summary = "preserved"
            attributes = {}

        metadata = Metadata()

    class FakeApplication:
        async def summarize(self, request):
            captured_request["request"] = request
            return FakeResult()

    def fail_catalogue_build():
        raise AssertionError("legacy request must not build catalogue")

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        fail_catalogue_build,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
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

    request = captured_request["request"]

    assert request.provider == "fake"
    assert request.model == "demo"


def test_model_configuration_loading_does_not_require_live_provider() -> None:
    script = read_script()

    assert 'fetch("/api/v1/product-config"' not in script

    assert '"/api/v1/product-config"' in script

    assert "OPENAI_API_KEY" not in script
    assert "OPENAI_BASE_URL" not in script
    assert "OPENAI_ORGANIZATION" not in script
