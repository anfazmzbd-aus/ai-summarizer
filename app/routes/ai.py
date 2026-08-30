"""
AI API routes.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.application_contracts import SummarizationApplicationRequest
from app.api.application import (
    ApplicationReviewRequiredError,
    build_summarization_application,
)
from app.api.schemas import (
    SummarizeError,
    SummarizeErrorResponse,
    SummarizeMetadata,
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

    try:
        application = build_summarization_application()
        result = await application.summarize(
            SummarizationApplicationRequest(
                text=request.text,
                provider=request.provider,
                model=request.model,
            )
        )
    except ApplicationReviewRequiredError:
        raise _product_error(
            status_code=409,
            code="REVIEW_REQUIRED",
            message="summarization requires review before execution",
        ) from None
    except ValueError:
        raise _product_error(
            status_code=422,
            code="INVALID_APPLICATION_STATE",
            message="summarization could not be authorized",
        ) from None
    except Exception:
        raise _product_error(
            status_code=500,
            code="SUMMARIZATION_FAILED",
            message="summarization could not be completed",
        ) from None

    return SummarizeResponse(
        summary=result.summary,
        model=result.model,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
        total_tokens=result.total_tokens,
        metadata=SummarizeMetadata(
            strategy=result.metadata.strategy,
            chunk_count=result.metadata.chunk_count,
            intelligence_mode=result.metadata.intelligence_mode,
            trace_id=result.metadata.trace_id,
            explainability_summary=result.metadata.explainability_summary,
            observability_status=result.metadata.attributes.get(
                "intelligence_observability_status"
            ),
            diagnostic_code=result.metadata.attributes.get(
                "intelligence_diagnostic_code"
            ),
            diagnostic_message=result.metadata.attributes.get(
                "intelligence_diagnostic_message"
            ),
        ),
    )


def _product_error(
    *,
    status_code: int,
    code: str,
    message: str,
) -> HTTPException:
    """Build a stable error without exposing implementation details."""

    return HTTPException(
        status_code=status_code,
        detail=SummarizeErrorResponse(
            error=SummarizeError(code=code, message=message)
        ).model_dump(),
    )
