"""V13 M4.4 safe model-selection frontend tests.

These tests certify that the frontend obtains product-safe model
options from the server catalogue and exposes them through an
accessible selector without exposing runtime provider configuration.

M4.4 intentionally does not yet route the selected product model into
the summarization request. Server-side resolution is introduced in
M4.5.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

TEMPLATE_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

SCRIPT_PATH = PROJECT_ROOT / "static" / "app.js"


def read_template() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")


def read_script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------


def test_frontend_contains_model_selection_control():
    html = read_template()

    assert 'id="modelSelection"' in html


def test_model_selection_has_product_model_name():
    html = read_template()

    assert 'name="product_model"' in html


def test_model_selection_has_accessible_label():
    html = read_template()

    assert '<label for="modelSelection">' in html
    assert "AI model" in html


def test_model_selection_has_accessible_help():
    html = read_template()

    assert 'id="modelSelectionHelp"' in html

    assert 'aria-describedby="modelSelectionHelp ' 'modelSelectionStatus"' in html


def test_model_selection_has_accessible_status():
    html = read_template()

    assert 'id="modelSelectionStatus"' in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html


def test_model_selection_starts_disabled():
    html = read_template()

    marker = 'id="modelSelection"'
    start = html.index(marker)

    select_fragment = html[start : start + 350]

    assert "disabled" in select_fragment


def test_model_selection_starts_with_loading_state():
    html = read_template()

    assert "Loading models..." in html
    assert "Loading available models..." in html


def test_frontend_does_not_hardcode_runtime_models_in_html():
    html = read_template()

    forbidden = (
        "gpt-5-mini",
        "gpt-5",
        "OPENAI_MODEL",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
    )

    for value in forbidden:
        assert value not in html


def test_frontend_does_not_expose_provider_selector():
    html = read_template()

    assert 'id="providerSelection"' not in html
    assert 'name="provider"' not in html


def test_frontend_does_not_expose_arbitrary_model_input():
    html = read_template()

    assert 'type="text" name="model"' not in html
    assert 'name="runtime_model"' not in html


# ---------------------------------------------------------------------------
# Product configuration loading
# ---------------------------------------------------------------------------


def test_script_references_product_config_endpoint():
    script = read_script()

    assert '"/api/v1/product-config"' in script


def test_script_uses_get_for_product_configuration():
    script = read_script()

    assert 'method: "GET"' in script


def test_script_requests_json_product_configuration():
    script = read_script()

    assert '"Accept": "application/json"' in script


def test_script_defines_model_loading_function():
    script = read_script()

    assert "async function loadProductModels()" in script


def test_script_loads_product_models_on_initialization():
    script = read_script()

    assert script.rstrip().endswith("loadProductModels();")


# ---------------------------------------------------------------------------
# Public model validation
# ---------------------------------------------------------------------------


def test_script_validates_public_model_shape():
    script = read_script()

    assert "function isValidPublicModel(model)" in script

    assert 'typeof model.id === "string"' in script
    assert 'typeof model.label === "string"' in script

    assert 'typeof model.is_default === "boolean"' in script


def test_script_rejects_empty_model_catalogue():
    script = read_script()

    assert "!Array.isArray(models) || " "models.length === 0" in script


def test_script_requires_exactly_one_default():
    script = read_script()

    assert "return defaults.length === 1;" in script


# ---------------------------------------------------------------------------
# Model option rendering
# ---------------------------------------------------------------------------


def test_script_creates_model_options():
    script = read_script()

    assert 'document.createElement("option")' in script


def test_model_option_value_uses_public_product_id():
    script = read_script()

    assert "option.value = model.id;" in script


def test_model_option_text_uses_public_label():
    script = read_script()

    assert "option.textContent = model.label;" in script


def test_default_model_is_selected_from_public_contract():
    script = read_script()

    assert "if (model.is_default)" in script
    assert "option.selected = true;" in script


def test_script_does_not_read_runtime_model_from_product_config():
    script = read_script()

    forbidden = (
        "model.model",
        "model.provider",
        "model.api_key",
        "model.base_url",
        "model.organization",
        "model.endpoint",
    )

    for value in forbidden:
        assert value not in script


# ---------------------------------------------------------------------------
# Frontend model state
# ---------------------------------------------------------------------------


def test_script_defines_model_state_contract():
    script = read_script()

    assert "const MODEL_STATE = Object.freeze({" in script
    assert 'LOADING: "loading"' in script
    assert 'READY: "ready"' in script
    assert 'ERROR: "error"' in script


def test_model_selector_is_enabled_when_ready():
    script = read_script()

    assert "modelSelection.disabled = false;" in script


def test_model_selector_is_disabled_on_error():
    script = read_script()

    error_marker = "if (nextState === MODEL_STATE.ERROR)"

    start = script.index(error_marker)

    fragment = script[start : start + 350]

    assert "modelSelection.disabled = true;" in fragment


def test_configuration_failure_has_safe_user_message():
    script = read_script()

    assert '"Model options are unavailable."' in script


def test_configuration_failure_does_not_surface_exception_text():
    script = read_script()

    assert "configurationError.message" not in script


def test_configuration_failure_replaces_options():
    script = read_script()

    assert '"Models unavailable"' in script


# ---------------------------------------------------------------------------
# Submission eligibility
# ---------------------------------------------------------------------------


def test_submission_requires_available_model():
    script = read_script()

    assert "function hasAvailableModel()" in script

    assert "currentModelState === MODEL_STATE.READY" in script


def test_submit_eligibility_includes_model_availability():
    script = read_script()

    assert "!hasAvailableModel()" in script


def test_model_change_updates_submit_eligibility():
    script = read_script()

    listener_start = script.index("modelSelection.addEventListener(")

    listener_end = script.index(
        ");",
        listener_start,
    )

    listener = script[listener_start : listener_end + 2]

    assert '"change"' in listener
    assert "updateSubmitEligibility();" in listener


def test_submission_guards_against_unavailable_model():
    script = read_script()

    assert (
        """if (!hasAvailableModel()) {
            modelSelection.focus();
            return;
        }"""
        in script
    )


# ---------------------------------------------------------------------------
# M4.4 architecture boundary
# ---------------------------------------------------------------------------


def test_m4_4_model_selection_uses_public_product_model_id():
    script = read_script()

    assert "modelSelection.value" in script

    assert "modelSelection.provider" not in script
    assert "modelSelection.model" not in script

    assert "dataset.provider" not in script
    assert "dataset.model" not in script


def test_m4_4_preserves_existing_fake_provider_contract():
    script = read_script()

    assert 'provider: "fake"' in script


def test_m4_4_preserves_existing_demo_model_contract():
    script = read_script()

    assert 'model: "demo"' in script


def test_frontend_does_not_construct_provider_configuration():
    script = read_script()

    forbidden = (
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_ORGANIZATION",
        "AI_PRODUCT_MODELS",
    )

    for value in forbidden:
        assert value not in script


def test_frontend_does_not_construct_runtime_model_mapping():
    script = read_script()

    assert "ProductModelCatalogue" not in script
    assert "build_product_model_catalogue" not in script


# ---------------------------------------------------------------------------
# Existing M3 control preservation
# ---------------------------------------------------------------------------


def test_summary_type_control_remains_present():
    html = read_template()

    assert 'id="summaryType"' in html
    assert 'value="general"' in html
    assert 'value="executive"' in html
    assert 'value="technical"' in html


def test_summary_length_control_remains_present():
    html = read_template()

    assert 'id="summaryLength"' in html
    assert 'value="short"' in html
    assert 'value="medium"' in html
    assert 'value="detailed"' in html


def test_custom_instructions_remain_present():
    html = read_template()

    assert 'id="customInstructions"' in html
    assert 'maxlength="2000"' in html


def test_existing_product_controls_remain_in_request():
    script = read_script()

    assert "summary_type: summaryType.value" in script
    assert "summary_length: summaryLength.value" in script

    assert "instructions: " "customInstructions.value.trim() || null" in script


# ---------------------------------------------------------------------------
# Real product-config integration
# ---------------------------------------------------------------------------


def test_product_config_endpoint_supports_frontend_loading(
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_PROVIDER",
        "fake",
    )

    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|runtime-a;" "fast|Fast|runtime-b",
    )

    response = client.get("/api/v1/product-config")

    assert response.status_code == 200

    assert response.json() == {
        "models": [
            {
                "id": "default",
                "label": "Default",
                "is_default": True,
            },
            {
                "id": "fast",
                "label": "Fast",
                "is_default": False,
            },
        ]
    }


def test_product_config_for_frontend_contains_no_runtime_mapping(
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_PROVIDER",
        "fake",
    )

    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|private-runtime-a;" "quality|Quality|private-runtime-b",
    )

    response = client.get("/api/v1/product-config")

    assert response.status_code == 200

    payload = response.json()

    for model in payload["models"]:
        assert set(model) == {
            "id",
            "label",
            "is_default",
        }

    assert "private-runtime-a" not in response.text
    assert "private-runtime-b" not in response.text
