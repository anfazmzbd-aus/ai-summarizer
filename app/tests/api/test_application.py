"""Tests for the canonical V11 summarization application boundary."""

from __future__ import annotations

from uuid import uuid4

import pytest
import asyncio

from app.ai import (
    SummarizationRequest,
    SummarizationResponse,
)
from app.api.application import (
    ApplicationReviewRequiredError,
    SummarizationApplication,
    build_summarization_application,
)
from app.core.application_contracts import (
    SummarizationApplicationRequest,
)
from app.core.intelligence_integration import ApplicationIntelligenceResult
from app.core.summarization_pipeline_factory import (
    build_summarization_pipeline_adapter,
)

from app.core.summarization_pipeline_adapter import (
    AsyncSummarizationPipelineAdapter,
)
from app.summarization.chunking.models import ChunkingConfig
from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.pipeline import SummarizationPipeline
from app.summarization.strategies.selector import (
    SummarizationStrategySelector,
)
from app.summarization.strategies.execution import StrategyExecutor
from app.summarization.strategies.models import (
    StrategySelectionConfig,
    SummarizationStrategyType,
)


def make_test_pipeline(
    *,
    max_tokens: int,
    direct_max_tokens: int,
    map_reduce_max_tokens: int,
) -> AsyncSummarizationPipelineAdapter:
    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=max_tokens,
            overlap_tokens=0,
        )
    )

    selector = SummarizationStrategySelector(
        StrategySelectionConfig(
            direct_max_tokens=direct_max_tokens,
            map_reduce_max_tokens=map_reduce_max_tokens,
        )
    )

    return AsyncSummarizationPipelineAdapter(
        SummarizationPipeline(
            chunker=chunker,
            selector=selector,
        )
    )


@pytest.mark.anyio
async def test_application_executes_map_reduce_through_existing_service() -> None:
    service = StubSummarizationService()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        make_test_pipeline(
            max_tokens=3,
            direct_max_tokens=3,
            map_reduce_max_tokens=10,
        ),
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="one two three four five six",
            provider="fake",
            model="demo",
        )
    )

    assert result.metadata.strategy == "map_reduce"
    assert result.metadata.chunk_count == 2

    # Two map calls + one reduce call.
    assert len(service.received_requests) == 3

    assert result.prompt_tokens == 30
    assert result.completion_tokens == 15
    assert result.total_tokens == 45


@pytest.mark.anyio
async def test_application_executes_hierarchical_through_existing_service() -> None:
    service = StubSummarizationService()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        make_test_pipeline(
            max_tokens=2,
            direct_max_tokens=2,
            map_reduce_max_tokens=4,
        ),
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="one two three four five six seven eight",
            provider="fake",
            model="demo",
        )
    )

    assert result.metadata.strategy == "hierarchical"
    assert result.metadata.chunk_count == 4

    assert len(service.received_requests) > 1

    assert result.prompt_tokens == (len(service.received_requests) * 10)
    assert result.completion_tokens == (len(service.received_requests) * 5)
    assert result.total_tokens == (result.prompt_tokens + result.completion_tokens)


@pytest.mark.anyio
async def test_application_returns_success_after_bounded_strategy_recovery() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class RecoveringStrategyExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)

            if strategy is SummarizationStrategyType.HIERARCHICAL:
                raise RuntimeError("internal hierarchical failure")

            return super().execute(
                strategy,
                chunks,
                summarize,
            )

    service = StubSummarizationService()

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=2,
            overlap_tokens=0,
        )
    )

    selector = SummarizationStrategySelector(
        StrategySelectionConfig(
            direct_max_tokens=2,
            map_reduce_max_tokens=4,
        )
    )

    pipeline = AsyncSummarizationPipelineAdapter(
        SummarizationPipeline(
            chunker=chunker,
            selector=selector,
            executor=RecoveringStrategyExecutor(),
        )
    )

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        pipeline,
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="one two three four five six seven eight",
            provider="fake",
            model="demo",
        )
    )

    assert isinstance(
        result.summary,
        str,
    )
    assert result.summary

    assert result.metadata.strategy == "hierarchical"

    assert executed_strategies == [
        SummarizationStrategyType.HIERARCHICAL,
        SummarizationStrategyType.MAP_REDUCE,
    ]

    assert len(service.received_requests) > 0
    assert result.prompt_tokens == (len(service.received_requests) * 10)
    assert result.completion_tokens == (len(service.received_requests) * 5)
    assert result.total_tokens == (result.prompt_tokens + result.completion_tokens)


@pytest.mark.anyio
async def test_application_repeated_bounded_recovery_remains_stable() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class RecoveringStrategyExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)

            if strategy is SummarizationStrategyType.HIERARCHICAL:
                raise RuntimeError("internal hierarchical failure")

            return super().execute(
                strategy,
                chunks,
                summarize,
            )

    service = StubSummarizationService()

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=2,
            overlap_tokens=0,
        )
    )

    selector = SummarizationStrategySelector(
        StrategySelectionConfig(
            direct_max_tokens=2,
            map_reduce_max_tokens=4,
        )
    )

    pipeline = AsyncSummarizationPipelineAdapter(
        SummarizationPipeline(
            chunker=chunker,
            selector=selector,
            executor=RecoveringStrategyExecutor(),
        )
    )

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        pipeline,
    )

    results = []

    for _ in range(5):
        result = await application.summarize(
            SummarizationApplicationRequest(
                text="one two three four five six seven eight",
                provider="fake",
                model="demo",
            )
        )

        results.append(result)

    assert (
        executed_strategies
        == [
            SummarizationStrategyType.HIERARCHICAL,
            SummarizationStrategyType.MAP_REDUCE,
        ]
        * 5
    )

    assert all(result.metadata.strategy == "hierarchical" for result in results)

    assert all(
        result.metadata.attributes["recovery_occurred"] == "true" for result in results
    )

    assert all(
        result.metadata.attributes["recovery_action"] == "fallback"
        for result in results
    )

    assert all(
        result.metadata.attributes["recovery_strategy"] == "map_reduce"
        for result in results
    )

    assert all(result.summary == results[0].summary for result in results)

    assert all(result.prompt_tokens == results[0].prompt_tokens for result in results)

    assert all(
        result.completion_tokens == results[0].completion_tokens for result in results
    )

    assert all(result.total_tokens == results[0].total_tokens for result in results)

    assert all(
        result.total_tokens == result.prompt_tokens + result.completion_tokens
        for result in results
    )


@pytest.mark.anyio
async def test_multi_call_pipeline_preserves_provider_and_model() -> None:
    service = StubSummarizationService()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        make_test_pipeline(
            max_tokens=3,
            direct_max_tokens=3,
            map_reduce_max_tokens=10,
        ),
    )

    await application.summarize(
        SummarizationApplicationRequest(
            text="one two three four five six",
            provider="fake",
            model="integration-model",
            prompt_name="summary",
        )
    )

    assert len(service.received_requests) > 1

    for request in service.received_requests:
        assert request.provider == "fake"
        assert request.model == "integration-model"
        assert request.prompt_name == "summary"


@pytest.mark.anyio
async def test_application_uses_resolved_service_model() -> None:
    service = StubSummarizationService()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="short text",
            provider="fake",
            model="demo",
        )
    )

    assert result.model == "demo"


class FailingSummarizationService:
    def __init__(self, message: str = "provider failure") -> None:
        self.message = message
        self.requests: list[SummarizationRequest] = []

    async def summarize(
        self,
        request: SummarizationRequest,
    ) -> SummarizationResponse:
        self.requests.append(request)
        raise RuntimeError(self.message)


@pytest.mark.anyio
async def test_application_propagates_direct_pipeline_failure() -> None:
    service = FailingSummarizationService()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="provider failure",
    ):
        await application.summarize(
            SummarizationApplicationRequest(
                text="short source text",
                provider="fake",
                model="demo",
            )
        )

    assert len(service.requests) == 1


@pytest.mark.anyio
async def test_application_propagates_map_reduce_failure() -> None:
    service = FailingSummarizationService(
        "map failure",
    )

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        make_test_pipeline(
            max_tokens=3,
            direct_max_tokens=3,
            map_reduce_max_tokens=10,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="map failure",
    ):
        await application.summarize(
            SummarizationApplicationRequest(
                text="one two three four five six",
                provider="fake",
                model="demo",
            )
        )

    assert len(service.requests) >= 1


def make_application(
    service: StubSummarizationService,
) -> SummarizationApplication:
    return SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
    )


class StubSummarizationService:
    def __init__(self) -> None:
        self.received_request: SummarizationRequest | None = None
        self.received_requests: list[SummarizationRequest] = []

    async def summarize(
        self,
        request: SummarizationRequest,
    ) -> SummarizationResponse:
        self.received_request = request
        self.received_requests.append(request)

        return SummarizationResponse(
            summary="stub summary",
            prompt="stub prompt",
            model=request.model,
            prompt_tokens=10,
            completion_tokens=5,
        )


class StubApplicationIntelligenceBoundary:
    def __init__(self) -> None:
        self.request: SummarizationApplicationRequest | None = None
        self.evaluate_count = 0
        self.result = ApplicationIntelligenceResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action="summarize",
            mode="preserve",
            execution_change_authorized=False,
            bounded_constraint_required=False,
            review_required=False,
            reasons=("existing execution behavior remains unchanged",),
            trace_id="trace-id",
            explainability_summary="existing execution behavior remains unchanged",
            observability_status="normal",
            diagnostic_code="INTELLIGENCE_NORMAL",
            diagnostic_message=(
                "intelligence lifecycle completed with normal execution-preserving behavior"
            ),
            reason_count=1,
        )

    def evaluate(
        self,
        request: SummarizationApplicationRequest,
    ) -> ApplicationIntelligenceResult:
        self.request = request
        self.evaluate_count += 1
        return self.result


def make_intelligence_result(
    mode: str,
    *,
    execution_change_authorized: bool = False,
    bounded_constraint_required: bool = False,
    review_required: bool = False,
) -> ApplicationIntelligenceResult:
    return ApplicationIntelligenceResult(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action="summarize",
        mode=mode,
        execution_change_authorized=execution_change_authorized,
        bounded_constraint_required=bounded_constraint_required,
        review_required=review_required,
        reasons=(f"{mode} application semantics",),
        trace_id="trace-id",
        explainability_summary=f"{mode} application semantics",
        observability_status="normal",
        diagnostic_code="INTELLIGENCE_NORMAL",
        diagnostic_message="test intelligence semantics",
        reason_count=1,
    )


@pytest.mark.anyio
async def test_application_executes_pipeline_through_existing_service() -> None:
    service = StubSummarizationService()
    application = make_application(service)  # type: ignore[arg-type]

    request = SummarizationApplicationRequest(
        text="Application boundary test.",
        provider="fake",
        model="demo",
    )

    result = await application.summarize(request)

    assert service.received_request is not None
    assert service.received_request.text == request.text
    assert service.received_request.provider == request.provider
    assert service.received_request.model == request.model

    assert result.summary == "stub summary"
    assert result.model == "demo"
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 5
    assert result.total_tokens == 15


@pytest.mark.anyio
async def test_application_exposes_read_only_intelligence_explainability_metadata() -> (
    None
):
    service = StubSummarizationService()
    application = make_application(service)  # type: ignore[arg-type]

    result = await application.summarize(
        SummarizationApplicationRequest(text="Explain the completed lifecycle.")
    )

    assert result.metadata.trace_id
    assert (
        result.metadata.trace_id
        == result.metadata.attributes["intelligence_context_id"]
    )
    assert result.metadata.explainability_summary
    assert result.metadata.attributes["intelligence_observability_status"] == "normal"
    assert result.metadata.attributes["intelligence_diagnostic_code"] == (
        "INTELLIGENCE_NORMAL"
    )
    assert int(result.metadata.attributes["intelligence_reason_count"]) > 0


@pytest.mark.anyio
async def test_application_translates_request_without_semantic_rewriting() -> None:
    service = StubSummarizationService()
    application = make_application(service)  # type: ignore[arg-type]

    request = SummarizationApplicationRequest(
        text="Exact source text.",
        provider="fake",
        model="test-model",
        prompt_name="summary",
    )

    await application.summarize(request)

    assert service.received_request is not None
    assert service.received_request.text == "Exact source text."
    assert service.received_request.provider == "fake"
    assert service.received_request.model == "test-model"
    assert service.received_request.prompt_name == "summary"


def test_build_summarization_application_returns_canonical_boundary() -> None:
    application = build_summarization_application()

    assert isinstance(
        application,
        SummarizationApplication,
    )


@pytest.mark.anyio
async def test_application_preserves_existing_default_prompt_when_unspecified() -> None:
    service = StubSummarizationService()
    application = make_application(service)  # type: ignore[arg-type]

    request = SummarizationApplicationRequest(
        text="Use the existing default prompt.",
        provider="fake",
        model="demo",
    )

    await application.summarize(request)

    assert service.received_request is not None
    assert service.received_request.prompt_name == "summary"


@pytest.mark.anyio
async def test_application_populates_pipeline_metadata() -> None:
    service = StubSummarizationService()
    pipeline = build_summarization_pipeline_adapter()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        pipeline,
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="Short source text.",
            provider="fake",
            model="demo",
        )
    )

    assert result.metadata.strategy == "direct"
    assert result.metadata.chunk_count == 1
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 5
    assert result.total_tokens == 15


@pytest.mark.anyio
async def test_application_records_post_execution_observation_and_feedback() -> None:
    service = StubSummarizationService()
    application = make_application(service)  # type: ignore[arg-type]

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="Record what happened after execution.",
            provider="fake",
            model="demo",
        )
    )

    attributes = result.metadata.attributes
    assert attributes["execution_id"]
    assert attributes["execution_outcome"] == "success"
    assert attributes["execution_evaluation_status"] == "unknown"
    assert attributes["execution_feedback_signals"] == "success,evaluation_unknown"


@pytest.mark.anyio
async def test_execution_feedback_does_not_reenter_intelligence_boundary() -> None:
    service = StubSummarizationService()
    intelligence = StubApplicationIntelligenceBoundary()
    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
        intelligence,  # type: ignore[arg-type]
    )

    await application.summarize(
        SummarizationApplicationRequest(text="Feedback is descriptive only.")
    )

    assert intelligence.request is not None
    assert intelligence.evaluate_count == 1


@pytest.mark.anyio
async def test_application_consumes_only_application_intelligence_projection() -> None:
    service = StubSummarizationService()
    intelligence = StubApplicationIntelligenceBoundary()
    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
        intelligence,  # type: ignore[arg-type]
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="Application intelligence boundary test.",
            provider="fake",
            model="demo",
        )
    )

    assert intelligence.request is not None
    assert result.metadata.intelligence_mode == "preserve"
    assert result.metadata.attributes["intelligence_context_id"] == str(
        intelligence.result.context_id
    )
    assert result.metadata.attributes["intelligence_correlation_id"] == str(
        intelligence.result.correlation_id
    )


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["preserve", "advisory"])
async def test_application_executes_for_non_review_intelligence_modes(
    mode: str,
) -> None:
    service = StubSummarizationService()
    intelligence = StubApplicationIntelligenceBoundary()
    intelligence.result = make_intelligence_result(mode)
    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
        intelligence,  # type: ignore[arg-type]
    )

    result = await application.summarize(
        SummarizationApplicationRequest(text="Non-review semantics.")
    )

    assert result.summary == "stub summary"
    assert service.received_request is not None
    assert result.metadata.intelligence_mode == mode


@pytest.mark.anyio
async def test_application_stops_before_execution_when_review_is_required() -> None:
    service = StubSummarizationService()
    intelligence = StubApplicationIntelligenceBoundary()
    intelligence.result = make_intelligence_result(
        "review",
        review_required=True,
    )
    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
        intelligence,  # type: ignore[arg-type]
    )

    with pytest.raises(
        ApplicationReviewRequiredError, match="requires intelligence review"
    ):
        await application.summarize(
            SummarizationApplicationRequest(text="Review first.")
        )

    assert service.received_request is None


@pytest.mark.anyio
async def test_application_rejects_authority_outside_constrained_mode() -> None:
    service = StubSummarizationService()
    intelligence = StubApplicationIntelligenceBoundary()
    intelligence.result = make_intelligence_result(
        "advisory",
        execution_change_authorized=True,
    )
    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
        intelligence,  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="only CONSTRAINED intelligence mode"):
        await application.summarize(
            SummarizationApplicationRequest(text="Invalid authority.")
        )

    assert service.received_request is None


@pytest.mark.anyio
async def test_application_requires_authority_for_constrained_mode() -> None:
    service = StubSummarizationService()
    intelligence = StubApplicationIntelligenceBoundary()
    intelligence.result = make_intelligence_result("constrained")
    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
        intelligence,  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="requires execution change authority"):
        await application.summarize(
            SummarizationApplicationRequest(text="Constrained later.")
        )

    assert service.received_request is None


@pytest.mark.anyio
async def test_application_accepts_validated_constrained_translation() -> None:
    service = StubSummarizationService()
    intelligence = StubApplicationIntelligenceBoundary()
    intelligence.result = make_intelligence_result(
        "constrained",
        execution_change_authorized=True,
        bounded_constraint_required=True,
    )
    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
        intelligence,  # type: ignore[arg-type]
    )

    result = await application.summarize(
        SummarizationApplicationRequest(text="Constrained translation.")
    )

    assert result.summary == "stub summary"
    assert service.received_request is not None
    assert result.metadata.intelligence_mode == "constrained"


@pytest.mark.anyio
async def test_application_rejects_constrained_mode_without_bounded_constraint() -> (
    None
):
    service = StubSummarizationService()
    intelligence = StubApplicationIntelligenceBoundary()
    intelligence.result = make_intelligence_result(
        "constrained",
        execution_change_authorized=True,
    )
    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
        intelligence,  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="requires bounded constraints"):
        await application.summarize(
            SummarizationApplicationRequest(text="Missing constraint.")
        )

    assert service.received_request is None


@pytest.mark.anyio
async def test_application_projects_product_safe_recovery_metadata() -> None:
    class RecoveringStrategyExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            if strategy is SummarizationStrategyType.HIERARCHICAL:
                raise RuntimeError("internal hierarchical failure")

            return super().execute(
                strategy,
                chunks,
                summarize,
            )

    service = StubSummarizationService()

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=2,
            overlap_tokens=0,
        )
    )

    selector = SummarizationStrategySelector(
        StrategySelectionConfig(
            direct_max_tokens=2,
            map_reduce_max_tokens=4,
        )
    )

    pipeline = AsyncSummarizationPipelineAdapter(
        SummarizationPipeline(
            chunker=chunker,
            selector=selector,
            executor=RecoveringStrategyExecutor(),
        )
    )

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        pipeline,
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="one two three four five six seven eight",
            provider="fake",
            model="demo",
        )
    )

    assert result.metadata.strategy == "hierarchical"

    attributes = result.metadata.attributes

    assert attributes["recovery_occurred"] == "true"
    assert attributes["recovery_action"] == "fallback"
    assert attributes["recovery_strategy"] == "map_reduce"


@pytest.mark.anyio
async def test_application_projects_no_recovery_metadata_for_normal_success() -> None:
    service = StubSummarizationService()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
    )

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="short source text",
            provider="fake",
            model="demo",
        )
    )

    attributes = result.metadata.attributes

    assert attributes["recovery_occurred"] == "false"
    assert attributes["recovery_action"] == ""
    assert attributes["recovery_strategy"] == ""


@pytest.mark.anyio
async def test_application_does_not_apply_strategy_recovery_to_provider_failure() -> (
    None
):
    service = FailingSummarizationService(
        "provider failure",
    )

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="provider failure",
    ):
        await application.summarize(
            SummarizationApplicationRequest(
                text="short source text",
                provider="fake",
                model="demo",
            )
        )

    assert len(service.requests) == 1


@pytest.mark.anyio
async def test_application_preserves_concurrent_request_isolation() -> None:
    class ConcurrentSummarizationService:
        def __init__(self) -> None:
            self.received_requests: list[SummarizationRequest] = []

        async def summarize(
            self,
            request: SummarizationRequest,
        ) -> SummarizationResponse:
            self.received_requests.append(request)

            delays = {
                "model-slow": 0.03,
                "model-medium": 0.02,
                "model-fast": 0.01,
            }

            await asyncio.sleep(delays[request.model])

            return SummarizationResponse(
                summary=f"summary:{request.text}",
                prompt="stub prompt",
                model=request.model,
                prompt_tokens={
                    "model-slow": 11,
                    "model-medium": 22,
                    "model-fast": 33,
                }[request.model],
                completion_tokens={
                    "model-slow": 1,
                    "model-medium": 2,
                    "model-fast": 3,
                }[request.model],
            )

    service = ConcurrentSummarizationService()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
    )

    slow_result, medium_result, fast_result = await asyncio.gather(
        application.summarize(
            SummarizationApplicationRequest(
                text="slow source",
                provider="fake",
                model="model-slow",
            )
        ),
        application.summarize(
            SummarizationApplicationRequest(
                text="medium source",
                provider="fake",
                model="model-medium",
            )
        ),
        application.summarize(
            SummarizationApplicationRequest(
                text="fast source",
                provider="fake",
                model="model-fast",
            )
        ),
    )

    assert slow_result.summary == "summary:slow source"
    assert slow_result.model == "model-slow"
    assert slow_result.prompt_tokens == 11
    assert slow_result.completion_tokens == 1

    assert medium_result.summary == "summary:medium source"
    assert medium_result.model == "model-medium"
    assert medium_result.prompt_tokens == 22
    assert medium_result.completion_tokens == 2

    assert fast_result.summary == "summary:fast source"
    assert fast_result.model == "model-fast"
    assert fast_result.prompt_tokens == 33
    assert fast_result.completion_tokens == 3

    assert len(service.received_requests) == 3

    assert {(request.text, request.model) for request in service.received_requests} == {
        ("slow source", "model-slow"),
        ("medium source", "model-medium"),
        ("fast source", "model-fast"),
    }


@pytest.mark.anyio
async def test_application_isolates_failure_between_concurrent_requests() -> None:
    class MixedOutcomeSummarizationService:
        async def summarize(
            self,
            request: SummarizationRequest,
        ) -> SummarizationResponse:
            await asyncio.sleep(0)

            if request.text == "failing source":
                raise RuntimeError("isolated provider failure")

            return SummarizationResponse(
                summary=f"summary:{request.text}",
                prompt="stub prompt",
                model=request.model,
                prompt_tokens=10,
                completion_tokens=5,
            )

    application = SummarizationApplication(
        MixedOutcomeSummarizationService(),  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
    )

    results = await asyncio.gather(
        application.summarize(
            SummarizationApplicationRequest(
                text="first source",
                provider="fake",
                model="model-one",
            )
        ),
        application.summarize(
            SummarizationApplicationRequest(
                text="failing source",
                provider="fake",
                model="model-fail",
            )
        ),
        application.summarize(
            SummarizationApplicationRequest(
                text="third source",
                provider="fake",
                model="model-three",
            )
        ),
        return_exceptions=True,
    )

    first_result, failed_result, third_result = results

    assert first_result.summary == "summary:first source"
    assert first_result.model == "model-one"

    assert isinstance(failed_result, RuntimeError)
    assert str(failed_result) == "isolated provider failure"

    assert third_result.summary == "summary:third source"
    assert third_result.model == "model-three"


@pytest.mark.anyio
async def test_application_repeated_large_hierarchical_requests_remain_stable() -> None:
    service = StubSummarizationService()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        make_test_pipeline(
            max_tokens=8,
            direct_max_tokens=8,
            map_reduce_max_tokens=16,
        ),
    )

    text = " ".join(f"token-{index}" for index in range(128))

    results = []

    for _ in range(5):
        result = await application.summarize(
            SummarizationApplicationRequest(
                text=text,
                provider="fake",
                model="reliability-model",
            )
        )

        results.append(result)

    assert all(result.metadata.strategy == "hierarchical" for result in results)

    assert all(
        result.metadata.chunk_count == results[0].metadata.chunk_count
        for result in results
    )

    assert results[0].metadata.chunk_count > 1

    assert all(result.summary == results[0].summary for result in results)

    assert all(result.model == "reliability-model" for result in results)

    assert all(result.prompt_tokens == results[0].prompt_tokens for result in results)

    assert all(
        result.completion_tokens == results[0].completion_tokens for result in results
    )

    assert all(result.total_tokens == results[0].total_tokens for result in results)

    assert all(
        result.total_tokens == result.prompt_tokens + result.completion_tokens
        for result in results
    )


@pytest.mark.anyio
async def test_application_remains_usable_after_sequential_provider_failure() -> None:
    class SequentialMixedOutcomeSummarizationService:
        def __init__(self) -> None:
            self.requests: list[SummarizationRequest] = []

        async def summarize(
            self,
            request: SummarizationRequest,
        ) -> SummarizationResponse:
            self.requests.append(request)

            if request.text == "failing source":
                raise RuntimeError("isolated provider failure")

            return SummarizationResponse(
                summary=f"summary:{request.text}",
                prompt="stub prompt",
                model=request.model,
                prompt_tokens=10,
                completion_tokens=5,
            )

    service = SequentialMixedOutcomeSummarizationService()

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        build_summarization_pipeline_adapter(),
    )

    first_result = await application.summarize(
        SummarizationApplicationRequest(
            text="first source",
            provider="fake",
            model="model-one",
        )
    )

    with pytest.raises(
        RuntimeError,
        match="isolated provider failure",
    ):
        await application.summarize(
            SummarizationApplicationRequest(
                text="failing source",
                provider="fake",
                model="model-fail",
            )
        )

    third_result = await application.summarize(
        SummarizationApplicationRequest(
            text="third source",
            provider="fake",
            model="model-three",
        )
    )

    assert first_result.summary == "summary:first source"
    assert first_result.model == "model-one"
    assert first_result.prompt_tokens == 10
    assert first_result.completion_tokens == 5
    assert first_result.total_tokens == 15

    assert third_result.summary == "summary:third source"
    assert third_result.model == "model-three"
    assert third_result.prompt_tokens == 10
    assert third_result.completion_tokens == 5
    assert third_result.total_tokens == 15

    assert [(request.text, request.model) for request in service.requests] == [
        ("first source", "model-one"),
        ("failing source", "model-fail"),
        ("third source", "model-three"),
    ]
