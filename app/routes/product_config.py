"""Product-safe frontend configuration route."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.product_config_schemas import (
    ProductConfigResponse,
    ProductModelOption,
)
from app.core.product_model_catalogue import (
    build_product_model_catalogue,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Product"],
)


@router.get(
    "/product-config",
    response_model=ProductConfigResponse,
)
def get_product_config() -> ProductConfigResponse:
    """Return presentation-safe product configuration.

    Runtime provider names, runtime model identifiers, credentials,
    endpoints, organization identifiers, and environment configuration
    remain server-private.
    """

    catalogue = build_product_model_catalogue()

    return ProductConfigResponse(
        models=[
            ProductModelOption(
                id=model.id,
                label=model.label,
                is_default=model.is_default,
            )
            for model in catalogue.models
        ]
    )
