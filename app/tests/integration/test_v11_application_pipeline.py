"""V11 M2 canonical application/pipeline integration tests."""

from __future__ import annotations

import pytest

from app.ai import SummarizationRequest, SummarizationResponse
from app.api.application import SummarizationApplication
from app.core.application_contracts import SummarizationApplicationRequest
from app.core.summarization_pipeline_adapter import (
    AsyncSummarizationPipelineAdapter,
)
from app.summarization.chunking.models import ChunkingConfig
from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.pipeline import SummarizationPipeline
from app.summarization.strategies.models import StrategySelectionConfig
from app.summarization.strategies.selector import (
    SummarizationStrategySelector,
)


class DeterministicService:
    def __init__(self) -> None:
        self.requests: list[SummarizationRequest] = []

    async def summarize(
        self,
        request: SummarizationRequest,
    ) -> SummarizationResponse:
        self.requests.append(request)

        return SummarizationResponse(
            summary=f"summary:{request.text}",
            prompt="test",
            model=request.model,
            prompt_tokens=2,
            completion_tokens=1,
        )


def build_application() -> tuple[
    SummarizationApplication,
    DeterministicService,
]:
    service = DeterministicService()

    pipeline = SummarizationPipeline(
        chunker=TextChunker(
            ChunkingConfig(
                max_tokens=3,
                overlap_tokens=0,
            )
        ),
        selector=SummarizationStrategySelector(
            StrategySelectionConfig(
                direct_max_tokens=3,
                map_reduce_max_tokens=10,
            )
        ),
    )

    return (
        SummarizationApplication(
            service,  # type: ignore[arg-type]
            AsyncSummarizationPipelineAdapter(pipeline),
        ),
        service,
    )


@pytest.mark.anyio
async def test_medium_text_traverses_real_v9_map_reduce_pipeline() -> None:
    application, service = build_application()

    result = await application.summarize(
        SummarizationApplicationRequest(
            text="one two three four five six",
            provider="fake",
            model="demo",
        )
    )

    assert result.metadata.strategy == "map_reduce"
    assert result.metadata.chunk_count == 2
    assert len(service.requests) == 3

    assert result.prompt_tokens == 6
    assert result.completion_tokens == 3
    assert result.total_tokens == 9
