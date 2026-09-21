"""Product-safe model catalogue and configuration policy."""

from __future__ import annotations

from dataclasses import dataclass
import os

from app.config.ai_settings import AISettings


_PRODUCT_MODELS_ENV = "AI_PRODUCT_MODELS"


@dataclass(frozen=True, slots=True)
class ProductModel:
    """Server-side approved product model mapping.

    ``id`` and ``label`` are product-facing metadata.

    ``provider`` and ``model`` are server-private runtime mapping
    information and must never be exposed directly through the public
    product configuration API.
    """

    id: str
    label: str
    provider: str
    model: str
    is_default: bool = False


class ProductModelCatalogue:
    """Authoritative catalogue of product-approved models."""

    def __init__(self, models: tuple[ProductModel, ...]) -> None:
        if not models:
            raise ValueError("product model catalogue cannot be empty")

        identifiers = [model.id for model in models]

        if len(identifiers) != len(set(identifiers)):
            raise ValueError("product model ids must be unique")

        defaults = [model for model in models if model.is_default]

        if len(defaults) != 1:
            raise ValueError("product model catalogue must contain exactly one default")

        self._models = models

    @property
    def models(self) -> tuple[ProductModel, ...]:
        """Return approved models in configured product order."""

        return self._models

    @property
    def default(self) -> ProductModel:
        """Return the single approved default model."""

        return next(model for model in self._models if model.is_default)

    def resolve(self, model_id: str) -> ProductModel:
        """Resolve an approved product model identifier.

        Unknown identifiers are rejected rather than passed through to
        the provider runtime.
        """

        for model in self._models:
            if model.id == model_id:
                return model

        raise ValueError("unsupported product model")


def build_product_model_catalogue(
    settings: AISettings | None = None,
) -> ProductModelCatalogue:
    """Build the authoritative product model catalogue.

    When ``AI_PRODUCT_MODELS`` is absent or blank, the application
    exposes one safe product option named ``default`` backed by the
    currently configured runtime model.

    When ``AI_PRODUCT_MODELS`` is configured, entries use:

        product-id|display-label|runtime-model

    Multiple entries are separated by semicolons.

    The first configured entry is the product default.

    Provider credentials and connection configuration remain owned by
    ``AISettings`` and are never encoded into this catalogue.
    """

    resolved_settings = settings or AISettings()

    provider = resolved_settings.provider.strip().lower()

    if provider == "fake":
        fallback_runtime_model = "demo"
    elif provider == "openai":
        fallback_runtime_model = resolved_settings.model.strip()

        if not fallback_runtime_model:
            raise ValueError("configured runtime model cannot be empty")
    else:
        raise ValueError("unsupported AI provider")

    configured_models = os.getenv(
        _PRODUCT_MODELS_ENV,
        "",
    ).strip()

    if not configured_models:
        return ProductModelCatalogue(
            (
                ProductModel(
                    id="default",
                    label="Default",
                    provider=provider,
                    model=fallback_runtime_model,
                    is_default=True,
                ),
            )
        )

    models = _parse_product_models(
        configured_models,
        provider=provider,
    )

    return ProductModelCatalogue(models)


def _parse_product_models(
    value: str,
    *,
    provider: str,
) -> tuple[ProductModel, ...]:
    """Parse administrator-approved product model configuration."""

    raw_entries = value.split(";")

    models: list[ProductModel] = []

    for index, raw_entry in enumerate(raw_entries):
        entry = raw_entry.strip()

        if not entry:
            raise ValueError("AI_PRODUCT_MODELS contains an empty entry")

        parts = entry.split("|")

        if len(parts) != 3:
            raise ValueError(
                "AI_PRODUCT_MODELS entries must use "
                "product-id|display-label|runtime-model"
            )

        product_id = parts[0].strip()
        label = parts[1].strip()
        runtime_model = parts[2].strip()

        if not product_id:
            raise ValueError("product model id cannot be empty")

        if not label:
            raise ValueError("product model label cannot be empty")

        if not runtime_model:
            raise ValueError("product runtime model cannot be empty")

        models.append(
            ProductModel(
                id=product_id,
                label=label,
                provider=provider,
                model=runtime_model,
                is_default=(index == 0),
            )
        )

    return tuple(models)
