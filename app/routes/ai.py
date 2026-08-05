"""
AI API routes.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.ai import SummarizationRequest
from app.api.dependencies import (
    build_summarization_service,
)
from app.api.schemas import (
    SummarizeRequest,
    SummarizeResponse,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["AI"],
)


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
)
async def summarize(
    request: SummarizeRequest,
) -> SummarizeResponse:

    service = build_summarization_service()

    result = await service.summarize(
        SummarizationRequest(
            text=request.text,
            provider=request.provider,
            model=request.model,
        )
    )

    return SummarizeResponse(
        summary=result.summary,
        model=result.model,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
        total_tokens=result.total_tokens,
    )
