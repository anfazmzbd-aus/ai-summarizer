"""
AI Summarizer V9.1

Production summarization API endpoint.

The endpoint supports:

    - deterministic MockProvider execution by default
    - explicit OpenRouter/OpenAI-compatible live execution

Provider selection is controlled through environment variables
rather than hard-coded credentials.
"""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.orchestration.contracts.execution_response import (
    ExecutionResponse,
)
from app.services.summarize_service import SummarizeService


router = APIRouter()


class Request(BaseModel):
    """
    Summarization request.
    """

    text: str


def _build_service() -> SummarizeService:
    """
    Build the appropriate summarization service.

    LIVE_PROVIDER controls whether the API uses a real
    OpenAI-compatible provider.

    Supported values:

        mock
        openai
        openrouter
    """

    provider = (
        os.getenv(
            "AI_PROVIDER",
            "mock",
        )
        .strip()
        .lower()
    )

    if provider == "mock":
        return SummarizeService()

    if provider == "openrouter":
        api_key = os.getenv(
            "OPENROUTER_API_KEY",
            "",
        ).strip()

        if not api_key:
            raise HTTPException(
                status_code=503,
                detail=(
                    "OpenRouter provider is enabled but "
                    "OPENROUTER_API_KEY is not configured."
                ),
            )

        model = os.getenv(
            "OPENROUTER_MODEL",
            "openai/gpt-5-mini",
        ).strip()

        endpoint = os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        ).strip()

        return SummarizeService.from_openrouter(
            api_key=api_key,
            model=model,
            endpoint=endpoint,
        )

    if provider == "openai":
        api_key = os.getenv(
            "OPENAI_API_KEY",
            "",
        ).strip()

        if not api_key:
            raise HTTPException(
                status_code=503,
                detail=(
                    "OpenAI provider is enabled but "
                    "OPENAI_API_KEY is not configured."
                ),
            )

        model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5",
        ).strip()

        endpoint = (
            os.getenv(
                "OPENAI_BASE_URL",
                "",
            ).strip()
            or None
        )

        organization = (
            os.getenv(
                "OPENAI_ORGANIZATION",
                "",
            ).strip()
            or None
        )

        return SummarizeService.from_openai(
            api_key=api_key,
            model=model,
            organization=organization,
            endpoint=endpoint,
        )

    raise HTTPException(
        status_code=500,
        detail=f"Unsupported AI_PROVIDER: {provider}",
    )


@router.post(
    "/summarize",
    response_model=ExecutionResponse,
)
def summarize(
    req: Request,
) -> ExecutionResponse:
    """
    Execute the summarization pipeline.
    """

    if not req.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text must not be empty.",
        )

    service = _build_service()

    return service.run(req.text)
