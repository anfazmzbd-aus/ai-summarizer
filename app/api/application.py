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
from app.core.summarization_pipeline_adapter import (
    AsyncSummarizationPipelineAdapter,
)
from app.core.summarization_pipeline_factory import (
    build_summarization_pipeline_adapter,
)
from app.core.application_metadata import (
    SummarizationExecutionMetadata,
)
from app.core.intelligence_integration import (
    ApplicationIntelligenceBoundary,
    ApplicationIntelligenceResult,
)


class ApplicationReviewRequiredError(RuntimeError):
    """Raised when intelligence requires review before summarization."""


class SummarizationApplication:
    """
    Stable application boundary for the canonical V11 summarization path.

    M3.1 composes the execution-neutral V10 intelligence handoff while
    isolating the public API from implementation-specific contracts.
    """

    def __init__(
        self,
        service: SummarizationService,
        pipeline: AsyncSummarizationPipelineAdapter,
        intelligence: ApplicationIntelligenceBoundary | None = None,
    ) -> None:
        self._service = service
        self._pipeline = pipeline
        self._intelligence = intelligence or ApplicationIntelligenceBoundary()

    async def summarize(
        self,
        request: SummarizationApplicationRequest,
    ) -> SummarizationApplicationResult:
        """Execute summarization through the canonical V9 pipeline."""
        intelligence_result = self._intelligence.evaluate(request)
        self._validate_intelligence_result(intelligence_result)

        if intelligence_result.mode == "review":
            raise ApplicationReviewRequiredError(
                "summarization requires intelligence review before execution"
            )

        prompt_tokens = 0
        completion_tokens = 0
        resolved_model = request.model or ""

        async def summarize_text(text: str) -> str:
            nonlocal prompt_tokens
            nonlocal completion_tokens
            nonlocal resolved_model
            if request.prompt_name is None:
                service_request = SummarizationRequest(
                    text=text,
                    provider=request.provider,
                    model=request.model,
                )
            else:
                service_request = SummarizationRequest(
                    text=text,
                    provider=request.provider,
                    model=request.model,
                    prompt_name=request.prompt_name,
                )

            service_result = await self._service.summarize(
                service_request,
            )

            prompt_tokens += service_result.prompt_tokens
            completion_tokens += service_result.completion_tokens
            resolved_model = service_result.model

            return service_result.summary

        pipeline_result = await self._pipeline.run(
            request.text,
            summarize_text,
        )

        return SummarizationApplicationResult(
            summary=pipeline_result.summary,
            model=resolved_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            metadata=SummarizationExecutionMetadata(
                strategy=pipeline_result.selection.strategy.value,
                chunk_count=pipeline_result.chunk_count,
                intelligence_mode=intelligence_result.mode,
                attributes={
                    "intelligence_context_id": str(intelligence_result.context_id),
                    "intelligence_correlation_id": str(
                        intelligence_result.correlation_id
                    ),
                },
            ),
        )

    @staticmethod
    def _validate_intelligence_result(
        result: ApplicationIntelligenceResult,
    ) -> None:
        """Validate application semantics before allowing pipeline execution."""
        if not isinstance(result, ApplicationIntelligenceResult):
            raise TypeError(
                "intelligence.evaluate must return an " "ApplicationIntelligenceResult"
            )

        if result.mode not in {"preserve", "advisory", "review"}:
            raise ValueError(
                "unsupported intelligence mode for M3.2 application semantics"
            )

        if result.execution_change_authorized:
            raise ValueError(
                "M3.2 application semantics cannot authorize execution changes"
            )

        expected_review_required = result.mode == "review"
        if result.review_required is not expected_review_required:
            raise ValueError(
                "intelligence review_required must match the application mode"
            )


def build_summarization_application() -> SummarizationApplication:
    """Build the canonical V11 summarization application."""

    return SummarizationApplication(
        build_summarization_service(),
        build_summarization_pipeline_adapter(),
    )
