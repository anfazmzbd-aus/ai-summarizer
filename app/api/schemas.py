"""
API schemas.
"""

from __future__ import annotations

from pydantic import BaseModel


class SummarizeRequest(BaseModel):

    text: str

    provider: str = "fake"

    model: str = "demo"


class SummarizeResponse(BaseModel):

    summary: str

    model: str

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int

    metadata: "SummarizeMetadata"


class SummarizeMetadata(BaseModel):
    """Product-safe projection of descriptive application metadata."""

    strategy: str | None = None
    chunk_count: int | None = None
    intelligence_mode: str | None = None
    trace_id: str | None = None
    explainability_summary: str | None = None
    observability_status: str | None = None
    diagnostic_code: str | None = None
    diagnostic_message: str | None = None

    recovery_occurred: bool | None = None
    recovery_action: str | None = None
    recovery_strategy: str | None = None


class SummarizeError(BaseModel):
    """Stable product-facing error details."""

    code: str
    message: str


class SummarizeErrorResponse(BaseModel):
    """Stable product-facing error envelope."""

    error: SummarizeError
