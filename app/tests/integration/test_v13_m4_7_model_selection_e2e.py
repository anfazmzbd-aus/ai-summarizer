"""V13 M4.7 end-to-end model-selection certification."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.product_model_catalogue import (
    ProductModel,
    ProductModelCatalogue,
)
from app.main import app
from app.routes import ai as ai_route
from app.routes import product_config as product_config_route


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "static" / "app.js"

client = TestClient(app)


def read_script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


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
    trace_id = "m4-7-trace"
    explainability_summary = "preserved"
    attributes = {}


class FakeResult:
    def __init__(
        self,
        *,
        model: str,
        summary: str = "certified summary",
    ) -> None:
        self.summary = summary
        self.model = model
        self.prompt_tokens = 20
        self.completion_tokens = 30
        self.metadata = FakeMetadata()

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def test_product_config_returns_approved_models_only(
    monkeypatch,
) -> None:
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


def test_public_configuration_contains_no_private_mapping(
    monkeypatch,
) -> None:
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
    assert '"provider"' not in serialized


def test_frontend_loads_product_configuration() -> None:
    script = read_script()

    assert '"/api/v1/product-config"' in script


def test_frontend_populates_model_id_and_label() -> None:
    script = read_script()

    assert "option.value = model.id;" in script
    assert "option.textContent = model.label;" in script


def test_frontend_honors_server_default() -> None:
    script = read_script()

    assert "if (model.is_default)" in script
    assert "option.selected = true;" in script


def test_frontend_requires_exactly_one_default() -> None:
    script = read_script()

    assert "defaults.length === 1" in script


def test_frontend_sends_selected_product_model() -> None:
    script = read_script()

    assert "product_model: modelSelection.value" in script


def test_frontend_does_not_construct_runtime_mapping() -> None:
    script = read_script()

    assert "model.provider" not in script
    assert "model.runtime_model" not in script
    assert "model.api_key" not in script
    assert "model.base_url" not in script


def test_approved_model_is_resolved_before_application(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()
    captured = {}

    class FakeApplication:
        async def summarize(self, request):
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
            "text": "Certification source",
            "product_model": "quality",
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.provider == "fake"
    assert request.model == "runtime-quality"


def test_default_product_model_resolves_to_default_runtime_model(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()
    captured = {}

    class FakeApplication:
        async def summarize(self, request):
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
            "text": "Certification source",
            "product_model": "balanced",
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.provider == "fake"
    assert request.model == "runtime-balanced"


def test_public_provider_cannot_override_selected_product_model(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()
    captured = {}

    class FakeApplication:
        async def summarize(self, request):
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
            "text": "Certification source",
            "provider": "attacker-provider",
            "model": "attacker-model",
            "product_model": "quality",
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.provider == "fake"
    assert request.model == "runtime-quality"


def test_unknown_product_model_is_rejected_before_application(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()
    application_called = False

    class FakeApplication:
        async def summarize(self, request):
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
            "text": "Certification source",
            "product_model": "unapproved",
        },
    )

    assert response.status_code == 422
    assert application_called is False


def test_unknown_model_response_is_product_safe(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Certification source",
            "product_model": "runtime-quality",
        },
    )

    assert response.status_code == 422

    payload = response.json()

    assert payload["detail"]["error"]["code"] == ("INVALID_APPLICATION_STATE")

    assert payload["detail"]["error"]["message"] == (
        "summarization could not be authorized"
    )


def test_unknown_model_response_does_not_leak_runtime_models(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Certification source",
            "product_model": "unapproved",
        },
    )

    serialized = response.text

    assert "runtime-balanced" not in serialized
    assert "runtime-quality" not in serialized
    assert "unsupported product model" not in serialized


def test_summary_controls_survive_model_resolution(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()
    captured = {}

    class FakeApplication:
        async def summarize(self, request):
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
            "text": "Certification source",
            "product_model": "quality",
            "summary_type": "executive",
            "summary_length": "detailed",
            "instructions": ("Focus on operational risks."),
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.summary_type.value == "executive"
    assert request.summary_length.value == "detailed"

    assert request.instructions == ("Focus on operational risks.")


def test_model_resolution_preserves_source_text(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()
    captured = {}

    class FakeApplication:
        async def summarize(self, request):
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

    source = "Exact certification source text."

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": source,
            "product_model": "quality",
        },
    )

    assert response.status_code == 200

    assert captured["request"].text == source


def test_response_reports_resolved_runtime_model(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()

    class FakeApplication:
        async def summarize(self, request):
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
            "text": "Certification source",
            "product_model": "quality",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["model"] == "runtime-quality"


def test_response_token_contract_is_preserved(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()

    class FakeApplication:
        async def summarize(self, request):
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
            "text": "Certification source",
            "product_model": "balanced",
        },
    )

    payload = response.json()

    assert payload["prompt_tokens"] == 20
    assert payload["completion_tokens"] == 30
    assert payload["total_tokens"] == 50


def test_legacy_request_still_bypasses_product_catalogue(
    monkeypatch,
) -> None:
    captured = {}

    class FakeApplication:
        async def summarize(self, request):
            captured["request"] = request

            return FakeResult(
                model=request.model or "",
                summary="legacy summary",
            )

    def fail_catalogue_build():
        raise AssertionError("legacy request must not use catalogue")

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

    request = captured["request"]

    assert request.provider == "fake"
    assert request.model == "demo"


def test_legacy_response_contract_is_preserved(
    monkeypatch,
) -> None:

    class FakeApplication:
        async def summarize(self, request):
            return FakeResult(
                model="demo",
                summary="legacy summary",
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

    payload = response.json()

    assert payload["summary"] == "legacy summary"
    assert payload["model"] == "demo"
    assert payload["total_tokens"] == 50


def test_frontend_fails_closed_when_models_are_unavailable() -> None:
    script = read_script()

    error_state_start = script.index("if (nextState === MODEL_STATE.ERROR)")

    fragment = script[error_state_start : error_state_start + 500]

    assert "modelSelection.disabled = true;" in fragment


def test_frontend_submit_requires_available_model() -> None:
    script = read_script()

    assert "!hasAvailableModel()" in script


def test_model_catalogue_is_not_a_second_summarization_path() -> None:
    script = read_script()

    assert 'fetch("/api/v1/summarize", {' in script

    assert "/api/v1/models/summarize" not in script
    assert "/api/v1/product-summarize" not in script


@pytest.mark.parametrize(
    "private_name",
    [
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_ORGANIZATION",
        "AI_PRODUCT_MODELS",
    ],
)
def test_frontend_contains_no_private_configuration_names(
    private_name: str,
) -> None:
    script = read_script()

    assert private_name not in script
