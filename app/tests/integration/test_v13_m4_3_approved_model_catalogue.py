"""V13 M4.3 approved product model catalogue tests.

These tests certify administrator-controlled model configuration while
preserving the public/private product security boundary established in
M4.2.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.config.ai_settings import AISettings
from app.core.product_model_catalogue import (
    ProductModelCatalogue,
    build_product_model_catalogue,
)
from app.main import app


client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def configure_fake_provider(monkeypatch) -> None:
    monkeypatch.setenv(
        "AI_PROVIDER",
        "fake",
    )


def configure_openai_provider(monkeypatch) -> None:
    monkeypatch.setenv(
        "AI_PROVIDER",
        "openai",
    )
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "configured-runtime-model",
    )


def get_product_config():
    return client.get("/api/v1/product-config")


# ---------------------------------------------------------------------------
# Default fallback behavior
# ---------------------------------------------------------------------------


def test_missing_product_model_configuration_uses_single_default(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.delenv(
        "AI_PRODUCT_MODELS",
        raising=False,
    )

    catalogue = build_product_model_catalogue()

    assert len(catalogue.models) == 1


def test_missing_configuration_uses_default_product_id(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.delenv(
        "AI_PRODUCT_MODELS",
        raising=False,
    )

    catalogue = build_product_model_catalogue()

    assert catalogue.default.id == "default"


def test_missing_configuration_uses_default_label(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.delenv(
        "AI_PRODUCT_MODELS",
        raising=False,
    )

    catalogue = build_product_model_catalogue()

    assert catalogue.default.label == "Default"


def test_fake_fallback_runtime_model_is_demo(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.delenv(
        "AI_PRODUCT_MODELS",
        raising=False,
    )

    catalogue = build_product_model_catalogue()

    assert catalogue.default.model == "demo"


def test_blank_product_model_configuration_uses_fallback(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "   ",
    )

    catalogue = build_product_model_catalogue()

    assert len(catalogue.models) == 1
    assert catalogue.default.id == "default"


def test_openai_fallback_uses_configured_runtime_model(
    monkeypatch,
):
    configure_openai_provider(monkeypatch)
    monkeypatch.delenv(
        "AI_PRODUCT_MODELS",
        raising=False,
    )

    catalogue = build_product_model_catalogue()

    assert catalogue.default.model == "configured-runtime-model"


# ---------------------------------------------------------------------------
# Multiple approved models
# ---------------------------------------------------------------------------


def test_multiple_approved_models_are_loaded(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|model-a;" "fast|Fast|model-b;" "quality|Quality|model-c",
    )

    catalogue = build_product_model_catalogue()

    assert len(catalogue.models) == 3


def test_configured_model_order_is_preserved(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|model-a;" "fast|Fast|model-b;" "quality|Quality|model-c",
    )

    catalogue = build_product_model_catalogue()

    assert [model.id for model in catalogue.models] == [
        "default",
        "fast",
        "quality",
    ]


def test_first_configured_model_is_default(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "quality|Quality|model-c;" "fast|Fast|model-b",
    )

    catalogue = build_product_model_catalogue()

    assert catalogue.default.id == "quality"


def test_only_first_configured_model_is_default(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|model-a;" "fast|Fast|model-b;" "quality|Quality|model-c",
    )

    catalogue = build_product_model_catalogue()

    defaults = [model for model in catalogue.models if model.is_default]

    assert len(defaults) == 1
    assert defaults[0].id == "default"


def test_runtime_models_are_preserved_server_side(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "fast|Fast|runtime-fast;" "quality|Quality|runtime-quality",
    )

    catalogue = build_product_model_catalogue()

    assert catalogue.resolve("fast").model == "runtime-fast"
    assert catalogue.resolve("quality").model == "runtime-quality"


def test_configured_models_use_active_provider(
    monkeypatch,
):
    configure_openai_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|runtime-a;" "quality|Quality|runtime-b",
    )

    catalogue = build_product_model_catalogue()

    assert all(model.provider == "openai" for model in catalogue.models)


# ---------------------------------------------------------------------------
# Configuration normalization
# ---------------------------------------------------------------------------


def test_configuration_whitespace_is_normalized(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "  default | Default Model | runtime-a ; " " fast | Fast Model | runtime-b  ",
    )

    catalogue = build_product_model_catalogue()

    assert catalogue.models[0].id == "default"
    assert catalogue.models[0].label == "Default Model"
    assert catalogue.models[0].model == "runtime-a"

    assert catalogue.models[1].id == "fast"
    assert catalogue.models[1].label == "Fast Model"
    assert catalogue.models[1].model == "runtime-b"


# ---------------------------------------------------------------------------
# Invalid administrator configuration
# ---------------------------------------------------------------------------


def test_duplicate_product_ids_are_rejected(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|model-a;" "default|Another|model-b",
    )

    with pytest.raises(
        ValueError,
        match="product model ids must be unique",
    ):
        build_product_model_catalogue()


def test_blank_product_id_is_rejected(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "|Default|model-a",
    )

    with pytest.raises(
        ValueError,
        match="product model id cannot be empty",
    ):
        build_product_model_catalogue()


def test_blank_product_label_is_rejected(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default||model-a",
    )

    with pytest.raises(
        ValueError,
        match="product model label cannot be empty",
    ):
        build_product_model_catalogue()


def test_blank_runtime_model_is_rejected(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|",
    )

    with pytest.raises(
        ValueError,
        match="product runtime model cannot be empty",
    ):
        build_product_model_catalogue()


def test_missing_configuration_component_is_rejected(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default",
    )

    with pytest.raises(
        ValueError,
        match="product-id\\|display-label\\|runtime-model",
    ):
        build_product_model_catalogue()


def test_extra_configuration_component_is_rejected(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|model-a|unexpected",
    )

    with pytest.raises(
        ValueError,
        match="product-id\\|display-label\\|runtime-model",
    ):
        build_product_model_catalogue()


def test_empty_configuration_entry_is_rejected(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|model-a;;fast|Fast|model-b",
    )

    with pytest.raises(
        ValueError,
        match="contains an empty entry",
    ):
        build_product_model_catalogue()


def test_trailing_configuration_separator_is_rejected(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|model-a;",
    )

    with pytest.raises(
        ValueError,
        match="contains an empty entry",
    ):
        build_product_model_catalogue()


def test_unsupported_provider_is_rejected(
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_PROVIDER",
        "unsupported-provider",
    )
    monkeypatch.delenv(
        "AI_PRODUCT_MODELS",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="unsupported AI provider",
    ):
        build_product_model_catalogue()


# ---------------------------------------------------------------------------
# Public API security boundary
# ---------------------------------------------------------------------------


def test_public_config_exposes_all_approved_product_options(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|private-runtime-a;"
        "fast|Fast|private-runtime-b;"
        "quality|Quality|private-runtime-c",
    )

    response = get_product_config()

    assert response.status_code == 200

    models = response.json()["models"]

    assert [model["id"] for model in models] == [
        "default",
        "fast",
        "quality",
    ]


def test_public_config_exposes_configured_labels(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Balanced|private-runtime-a;" "fast|Fast|private-runtime-b",
    )

    response = get_product_config()

    models = response.json()["models"]

    assert [model["label"] for model in models] == [
        "Balanced",
        "Fast",
    ]


def test_public_config_exposes_only_safe_model_fields(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|private-runtime-a;" "fast|Fast|private-runtime-b",
    )

    response = get_product_config()

    assert response.status_code == 200

    for model in response.json()["models"]:
        assert set(model) == {
            "id",
            "label",
            "is_default",
        }


def test_public_config_does_not_expose_runtime_model_names(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|private-runtime-a;" "fast|Fast|private-runtime-b",
    )

    response = get_product_config()

    assert "private-runtime-a" not in response.text
    assert "private-runtime-b" not in response.text


def test_public_config_does_not_expose_provider_name(
    monkeypatch,
):
    configure_openai_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|private-runtime-a",
    )

    response = get_product_config()

    assert response.status_code == 200

    model = response.json()["models"][0]

    assert "provider" not in model
    assert "openai" not in response.text.lower()


def test_public_config_does_not_expose_credentials(
    monkeypatch,
):
    configure_openai_provider(monkeypatch)
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "m4-private-secret",
    )
    monkeypatch.setenv(
        "OPENAI_BASE_URL",
        "https://private.example.invalid/v1",
    )
    monkeypatch.setenv(
        "OPENAI_ORGANIZATION",
        "private-organization",
    )
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|private-runtime-a",
    )

    response = get_product_config()

    assert response.status_code == 200

    assert "m4-private-secret" not in response.text
    assert "private.example.invalid" not in response.text
    assert "private-organization" not in response.text


# ---------------------------------------------------------------------------
# Resolution contract for future M4.5 enforcement
# ---------------------------------------------------------------------------


def test_catalogue_resolves_each_approved_product_id(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|runtime-a;" "fast|Fast|runtime-b;" "quality|Quality|runtime-c",
    )

    catalogue = build_product_model_catalogue()

    assert catalogue.resolve("default").model == "runtime-a"
    assert catalogue.resolve("fast").model == "runtime-b"
    assert catalogue.resolve("quality").model == "runtime-c"


def test_catalogue_rejects_unapproved_product_id(
    monkeypatch,
):
    configure_fake_provider(monkeypatch)
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|runtime-a",
    )

    catalogue: ProductModelCatalogue = build_product_model_catalogue()

    with pytest.raises(
        ValueError,
        match="unsupported product model",
    ):
        catalogue.resolve("arbitrary-provider-model")


# ---------------------------------------------------------------------------
# Explicit settings injection
# ---------------------------------------------------------------------------


def test_catalogue_supports_explicit_settings_injection(
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_PRODUCT_MODELS",
        "default|Default|runtime-a",
    )

    settings = AISettings(
        provider="fake",
        api_key="",
        model="ignored-for-configured-catalogue",
        base_url=None,
        organization=None,
    )

    catalogue = build_product_model_catalogue(
        settings=settings,
    )

    assert catalogue.default.provider == "fake"
    assert catalogue.default.model == "runtime-a"
