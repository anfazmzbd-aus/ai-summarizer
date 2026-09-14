"""
API schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator

from app.core.product_options import SummaryLength, SummaryType


class SummarizeRequest(BaseModel):

    text: str

    provider: str = "fake"

    model: str = "demo"

    summary_type: SummaryType = SummaryType.GENERAL

    summary_length: SummaryLength = SummaryLength.MEDIUM

    instructions: str | None = None

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty")
        return value

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            return None

        if len(normalized) > 2000:
            raise ValueError("instructions must not exceed 2000 characters")

        return normalized


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
