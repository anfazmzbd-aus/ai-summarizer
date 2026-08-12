"""
AI Summarizer V9.1

Summarization API endpoint.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
)
from pydantic import (
    BaseModel,
)

from app.orchestration.contracts.execution_response import (
    ExecutionResponse,
)
from app.services.summarize_service import (
    SummarizeService,
)


router = APIRouter()


class SummarizeRequest(BaseModel):
    """Request payload for the summarization endpoint."""

    text: str


@router.post(
    "/summarize",
    response_model=ExecutionResponse,
)
def summarize(
    req: SummarizeRequest,
) -> ExecutionResponse:
    """
    Execute the deterministic/default V9 summarization runtime.

    The endpoint exposes the complete ExecutionResponse contract.
    """

    service = SummarizeService()

    return service.run(req.text)
