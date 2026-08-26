"""Canonical V11 summarization application boundary."""

from __future__ import annotations

from app.ai import (
    SummarizationRequest,
    SummarizationService,
)
from app.api.dependencies import build_summarization_service
from app.core.application_contracts import (
    SummarizationApplicationRequest,
    SummarizationApplicationResult,
)


class SummarizationApplication:
    """
    Stable application boundary for the canonical V11 summarization path.

    M1 preserves existing V10 summarization behavior while isolating the
    public API from implementation-specific summarization contracts.
    """

    def __init__(
        self,
        service: SummarizationService,
    ) -> None:
        self._service = service

    async def summarize(
        self,
        request: SummarizationApplicationRequest,
    ) -> SummarizationApplicationResult:
        """Execute summarization through the current V10 service."""

        if request.prompt_name is None:
            service_request = SummarizationRequest(
                text=request.text,
                provider=request.provider,
                model=request.model,
            )
        else:
            service_request = SummarizationRequest(
                text=request.text,
                provider=request.provider,
                model=request.model,
                prompt_name=request.prompt_name,
            )

        result = await self._service.summarize(service_request)

        return SummarizationApplicationResult(
            summary=result.summary,
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
        )


def build_summarization_application() -> SummarizationApplication:
    """Build the canonical V11 summarization application."""

    return SummarizationApplication(
        build_summarization_service(),
    )
