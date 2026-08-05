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
