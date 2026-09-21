"""V13 M4.2 product configuration endpoint integration tests.

These tests certify the product-safe model catalogue boundary.

The public product configuration endpoint may expose presentation-safe
model metadata, but it must never expose provider credentials, runtime
connection details, or other server-private configuration.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.core.product_model_catalogue import (
    ProductModel,
    ProductModelCatalogue,
)
from app.main import app


client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_product_config():
    """Fetch the public product configuration."""

    return client.get("/api/v1/product-config")


def build_model(
    *,
    model_id: str = "default",
    label: str = "Default",
    provider: str = "fake",
    model: str = "demo",
    is_default: bool = True,
) -> ProductModel:
    """Build a product model for catalogue contract tests."""

    return ProductModel(
        id=model_id,
        label=label,
        provider=provider,
        model=model,
        is_default=is_default,
    )


# ---------------------------------------------------------------------------
# Public endpoint contract
# ---------------------------------------------------------------------------


def test_product_config_endpoint_returns_200(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    assert response.status_code == 200


def test_product_config_response_contains_models(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    payload = response.json()

    assert "models" in payload


def test_product_config_catalogue_is_not_empty(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    models = response.json()["models"]

    assert models


def test_product_config_contains_exactly_one_default(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    models = response.json()["models"]
    defaults = [model for model in models if model["is_default"]]

    assert len(defaults) == 1


def test_product_config_default_id_is_default(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    models = response.json()["models"]
    default_model = next(model for model in models if model["is_default"])

    assert default_model["id"] == "default"


def test_product_config_default_label_is_default(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    models = response.json()["models"]
    default_model = next(model for model in models if model["is_default"])

    assert default_model["label"] == "Default"


def test_public_model_contains_id(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    model = response.json()["models"][0]

    assert "id" in model


def test_public_model_contains_label(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    model = response.json()["models"][0]

    assert "label" in model


def test_public_model_contains_is_default(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    model = response.json()["models"][0]

    assert "is_default" in model


# ---------------------------------------------------------------------------
# Security boundary
# ---------------------------------------------------------------------------


def test_product_config_does_not_expose_provider(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    model = response.json()["models"][0]

    assert "provider" not in model


def test_product_config_does_not_expose_runtime_model(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    model = response.json()["models"][0]

    # Public "id" identifies the product option.
    # The private runtime "model" field must not cross the boundary.
    assert "model" not in model


def test_product_config_does_not_expose_api_key(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "m4-secret-api-key",
    )

    response = get_product_config()

    payload = response.json()
    model = payload["models"][0]

    assert "api_key" not in model
    assert "m4-secret-api-key" not in response.text


def test_product_config_does_not_expose_base_url(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")
    monkeypatch.setenv(
        "OPENAI_BASE_URL",
        "https://private.example.invalid/v1",
    )

    response = get_product_config()

    payload = response.json()
    model = payload["models"][0]

    assert "base_url" not in model
    assert "https://private.example.invalid/v1" not in response.text


def test_product_config_does_not_expose_organization(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")
    monkeypatch.setenv(
        "OPENAI_ORGANIZATION",
        "private-organization",
    )

    response = get_product_config()

    payload = response.json()
    model = payload["models"][0]

    assert "organization" not in model
    assert "private-organization" not in response.text


def test_product_config_does_not_expose_endpoint(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    model = response.json()["models"][0]

    assert "endpoint" not in model


def test_product_config_does_not_expose_environment_variable_names(
    monkeypatch,
):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    response = get_product_config()

    public_payload = response.text

    forbidden_names = (
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL",
        "OPENAI_ORGANIZATION",
        "AI_PROVIDER",
    )

    for name in forbidden_names:
        assert name not in public_payload


def test_fake_product_config_requires_no_provider_credentials(
    monkeypatch,
):
    monkeypatch.setenv("AI_PROVIDER", "fake")

    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )
    monkeypatch.delenv(
        "OPENAI_BASE_URL",
        raising=False,
    )
    monkeypatch.delenv(
        "OPENAI_ORGANIZATION",
        raising=False,
    )

    response = get_product_config()

    assert response.status_code == 200
    assert response.json()["models"]


# ---------------------------------------------------------------------------
# Catalogue invariants
# ---------------------------------------------------------------------------


def test_catalogue_rejects_duplicate_model_ids():
    first = build_model(
        model_id="default",
        label="Default",
        is_default=True,
    )

    second = build_model(
        model_id="default",
        label="Duplicate",
        model="other-model",
        is_default=False,
    )

    with pytest.raises(
        ValueError,
        match="product model ids must be unique",
    ):
        ProductModelCatalogue(
            (
                first,
                second,
            )
        )


def test_catalogue_rejects_zero_defaults():
    first = build_model(
        model_id="model-a",
        label="Model A",
        model="model-a",
        is_default=False,
    )

    second = build_model(
        model_id="model-b",
        label="Model B",
        model="model-b",
        is_default=False,
    )

    with pytest.raises(
        ValueError,
        match="exactly one default",
    ):
        ProductModelCatalogue(
            (
                first,
                second,
            )
        )


def test_catalogue_rejects_multiple_defaults():
    first = build_model(
        model_id="model-a",
        label="Model A",
        model="model-a",
        is_default=True,
    )

    second = build_model(
        model_id="model-b",
        label="Model B",
        model="model-b",
        is_default=True,
    )

    with pytest.raises(
        ValueError,
        match="exactly one default",
    ):
        ProductModelCatalogue(
            (
                first,
                second,
            )
        )


def test_catalogue_resolves_approved_model_id():
    expected = build_model()

    catalogue = ProductModelCatalogue((expected,))

    resolved = catalogue.resolve("default")

    assert resolved == expected


def test_catalogue_rejects_unknown_model_id():
    catalogue = ProductModelCatalogue((build_model(),))

    with pytest.raises(
        ValueError,
        match="unsupported product model",
    ):
        catalogue.resolve("not-approved")
