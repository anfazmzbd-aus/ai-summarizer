"""V11 M2.4 canonical API/V9-pipeline integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

import app.routes.ai as ai_routes
from app.ai import (
    SummarizationRequest,
    SummarizationResponse,
)
from app.api.application import SummarizationApplication
from app.main import app
from app.core.summarization_pipeline_adapter import (
    AsyncSummarizationPipelineAdapter,
)
from app.summarization.chunking.models import ChunkingConfig
from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.pipeline import SummarizationPipeline
from app.summarization.strategies.models import (
    StrategySelectionConfig,
)
from app.summarization.strategies.selector import (
    SummarizationStrategySelector,
)


class DeterministicSummarizationService:
    def __init__(self) -> None:
        self.requests: list[SummarizationRequest] = []

    async def summarize(
        self,
        request: SummarizationRequest,
    ) -> SummarizationResponse:
        self.requests.append(request)

        return SummarizationResponse(
            summary=f"summary:{request.text}",
            prompt="integration prompt",
            model=request.model,
            prompt_tokens=2,
            completion_tokens=1,
        )


def build_test_application(
    *,
    max_tokens: int,
    direct_max_tokens: int,
    map_reduce_max_tokens: int,
) -> tuple[
    SummarizationApplication,
    DeterministicSummarizationService,
]:
    service = DeterministicSummarizationService()

    pipeline = SummarizationPipeline(
        chunker=TextChunker(
            ChunkingConfig(
                max_tokens=max_tokens,
                overlap_tokens=0,
            )
        ),
        selector=SummarizationStrategySelector(
            StrategySelectionConfig(
                direct_max_tokens=direct_max_tokens,
                map_reduce_max_tokens=map_reduce_max_tokens,
            )
        ),
    )

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        AsyncSummarizationPipelineAdapter(pipeline),
    )

    return application, service


def test_short_text_traverses_canonical_api_and_direct_pipeline(
    monkeypatch,
) -> None:
    application, service = build_test_application(
        max_tokens=5,
        direct_max_tokens=5,
        map_reduce_max_tokens=20,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "one two three",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["summary"] == "summary:one two three"
    assert body["model"] == "demo"
    assert body["prompt_tokens"] == 2
    assert body["completion_tokens"] == 1
    assert body["total_tokens"] == 3

    assert len(service.requests) == 1


def test_medium_text_traverses_canonical_api_and_map_reduce_pipeline(
    monkeypatch,
) -> None:
    application, service = build_test_application(
        max_tokens=3,
        direct_max_tokens=3,
        map_reduce_max_tokens=10,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "one two three four five six",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    body = response.json()

    # Two map calls + one reduce call.
    assert len(service.requests) == 3

    assert body["model"] == "demo"
    assert body["prompt_tokens"] == 6
    assert body["completion_tokens"] == 3
    assert body["total_tokens"] == 9


def test_long_text_traverses_canonical_api_and_hierarchical_pipeline(
    monkeypatch,
) -> None:
    application, service = build_test_application(
        max_tokens=2,
        direct_max_tokens=2,
        map_reduce_max_tokens=4,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "one two three four five six seven eight",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(service.requests) > 1

    assert body["prompt_tokens"] == len(service.requests) * 2
    assert body["completion_tokens"] == len(service.requests)
    assert body["total_tokens"] == len(service.requests) * 3


def test_api_pipeline_preserves_provider_and_model_across_all_calls(
    monkeypatch,
) -> None:
    application, service = build_test_application(
        max_tokens=3,
        direct_max_tokens=3,
        map_reduce_max_tokens=10,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "one two three four five six",
            "provider": "fake",
            "model": "integration-model",
        },
    )

    assert response.status_code == 200
    assert len(service.requests) == 3

    for request in service.requests:
        assert request.provider == "fake"
        assert request.model == "integration-model"


class FailingSummarizationService:
    async def summarize(
        self,
        request: SummarizationRequest,
    ) -> SummarizationResponse:
        raise RuntimeError("provider failure")


def test_canonical_api_surfaces_pipeline_failure(
    monkeypatch,
) -> None:
    service = FailingSummarizationService()

    pipeline = AsyncSummarizationPipelineAdapter(
        SummarizationPipeline(
            chunker=TextChunker(
                ChunkingConfig(
                    max_tokens=5,
                    overlap_tokens=0,
                )
            ),
            selector=SummarizationStrategySelector(
                StrategySelectionConfig(
                    direct_max_tokens=5,
                    map_reduce_max_tokens=20,
                )
            ),
        )
    )

    application = SummarizationApplication(
        service,  # type: ignore[arg-type]
        pipeline,
    )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "one two three",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 500
