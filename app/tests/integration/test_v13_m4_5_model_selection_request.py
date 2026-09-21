"""V13 M4.5 canonical model-selection request integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.schemas import SummarizeRequest
from app.core.product_model_catalogue import (
    ProductModel,
    ProductModelCatalogue,
)
from app.main import app
from app.routes import ai as ai_route


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "static" / "app.js"

client = TestClient(app)


def read_script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_request_schema_accepts_product_model() -> None:
    request = SummarizeRequest(
        text="Example source",
        product_model="quality",
    )

    assert request.product_model == "quality"


def test_product_model_is_optional_for_legacy_requests() -> None:
    request = SummarizeRequest(
        text="Example source",
    )

    assert request.product_model is None


def test_product_model_is_trimmed() -> None:
    request = SummarizeRequest(
        text="Example source",
        product_model="  quality  ",
    )

    assert request.product_model == "quality"


def test_blank_product_model_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="product_model must not be empty",
    ):
        SummarizeRequest(
            text="Example source",
            product_model="   ",
        )


def test_frontend_sends_selected_product_model() -> None:
    script = read_script()

    assert "product_model: modelSelection.value" in script


def test_frontend_preserves_canonical_summarize_endpoint() -> None:
    script = read_script()

    assert 'fetch("/api/v1/summarize"' in script


def test_frontend_does_not_send_private_provider_from_model_option() -> None:
    script = read_script()

    assert "modelSelection.provider" not in script
    assert "modelSelection.dataset.provider" not in script


def test_frontend_does_not_send_private_runtime_model_from_option() -> None:
    script = read_script()

    assert "modelSelection.model" not in script
    assert "modelSelection.dataset.model" not in script


def test_frontend_preserves_summary_type() -> None:
    script = read_script()

    assert "summary_type: summaryType.value" in script


def test_frontend_preserves_summary_length() -> None:
    script = read_script()

    assert "summary_length: summaryLength.value" in script


def test_frontend_preserves_custom_instructions() -> None:
    script = read_script()

    assert "instructions: customInstructions.value.trim() || null" in script


def test_catalogue_resolves_approved_product_id() -> None:
    catalogue = ProductModelCatalogue(
        (
            ProductModel(
                id="default",
                label="Default",
                provider="fake",
                model="demo",
                is_default=True,
            ),
            ProductModel(
                id="quality",
                label="Quality",
                provider="fake",
                model="quality-runtime",
            ),
        )
    )

    resolved = catalogue.resolve("quality")

    assert resolved.provider == "fake"
    assert resolved.model == "quality-runtime"


def test_catalogue_rejects_unknown_product_id() -> None:
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
        catalogue.resolve("arbitrary-runtime-model")


def test_product_model_path_overrides_public_provider_and_model(
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
            "provider": "untrusted-provider",
            "model": "untrusted-model",
            "product_model": "approved",
        },
    )

    assert response.status_code == 200

    application_request = captured_request["request"]

    assert application_request.provider == "fake"
    assert application_request.model == "approved-runtime-model"


def test_product_model_path_preserves_summary_controls(
    monkeypatch,
) -> None:
    captured_request = {}

    class FakeResult:
        summary = "approved summary"
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
            "product_model": "default",
            "summary_type": "executive",
            "summary_length": "detailed",
            "instructions": "Focus on commercial risk.",
        },
    )

    assert response.status_code == 200

    application_request = captured_request["request"]

    assert application_request.summary_type.value == "executive"
    assert application_request.summary_length.value == "detailed"
    assert application_request.instructions == "Focus on commercial risk."


def test_unknown_product_model_is_rejected_before_application_execution(
    monkeypatch,
) -> None:
    application_called = False

    class FakeApplication:
        async def summarize(self, request):
            nonlocal application_called
            application_called = True
            raise AssertionError(
                "application must not execute for an unknown product model"
            )

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
            "product_model": "not-approved",
        },
    )

    assert response.status_code == 422
    assert application_called is False


def test_unknown_product_model_returns_stable_safe_error(
    monkeypatch,
) -> None:
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

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Example source",
            "product_model": "private-runtime-model",
        },
    )

    assert response.status_code == 422

    payload = response.json()

    assert payload["detail"]["error"]["code"] == ("INVALID_APPLICATION_STATE")
    assert payload["detail"]["error"]["message"] == (
        "summarization could not be authorized"
    )

    serialized = str(payload)

    assert "unsupported product model" not in serialized


def test_legacy_request_does_not_require_catalogue(
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

    def fail_if_catalogue_is_built():
        raise AssertionError("legacy request must not require product catalogue")

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        fail_if_catalogue_is_built,
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

    application_request = captured_request["request"]

    assert application_request.provider == "fake"
    assert application_request.model == "demo"


def test_legacy_response_contract_remains_available(
    monkeypatch,
) -> None:

    class FakeResult:
        summary = "legacy summary"
        model = "demo"
        prompt_tokens = 20
        completion_tokens = 30

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
            return FakeResult()

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
    assert payload["prompt_tokens"] == 20
    assert payload["completion_tokens"] == 30
    assert payload["total_tokens"] == 50


def test_product_model_not_added_to_application_contract() -> None:
    from dataclasses import fields

    from app.core.application_contracts import (
        SummarizationApplicationRequest,
    )

    field_names = {field.name for field in fields(SummarizationApplicationRequest)}

    assert "product_model" not in field_names


def test_private_catalogue_mapping_stays_outside_application_contract() -> None:
    from dataclasses import fields

    from app.core.application_contracts import (
        SummarizationApplicationRequest,
    )

    field_names = {field.name for field in fields(SummarizationApplicationRequest)}

    assert "provider" in field_names
    assert "model" in field_names
    assert "product_model" not in field_names
