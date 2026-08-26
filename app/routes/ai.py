"""
AI API routes.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.application_contracts import SummarizationApplicationRequest
from app.api.application import (
    build_summarization_application,
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

    application = build_summarization_application()

    result = await application.summarize(
        SummarizationApplicationRequest(
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
