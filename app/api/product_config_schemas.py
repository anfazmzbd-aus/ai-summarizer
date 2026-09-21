"""Product-safe configuration response contracts."""

from __future__ import annotations

from pydantic import BaseModel


class ProductModelOption(BaseModel):
    id: str
    label: str
    is_default: bool


class ProductConfigResponse(BaseModel):
    models: list[ProductModelOption]
