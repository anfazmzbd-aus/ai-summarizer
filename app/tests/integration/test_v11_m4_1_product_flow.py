"""V11 M4.1 canonical product-flow boundary tests."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import app.routes.ai as ai_routes
from app.ai import SummarizationRequest, SummarizationResponse
from app.api.application import SummarizationApplication
from app.core.summarization_pipeline_adapter import (
    AsyncSummarizationPipelineAdapter,
)
from app.main import app
from app.summarization.chunking.models import ChunkingConfig
from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.pipeline import SummarizationPipeline
from app.summarization.strategies.models import StrategySelectionConfig
from app.summarization.strategies.selector import SummarizationStrategySelector


REALISTIC_TEXT = (
    "The neighborhood library launched a weekend repair clinic for small "
    "appliances. Volunteers teach residents how to diagnose common faults, "
    "replace safe-to-service parts, and reuse equipment that would otherwise "
    "be discarded. The first three sessions filled quickly, so the library "
    "plans to publish a recurring schedule and collect feedback from visitors."
)
ROOT = Path(__file__).resolve().parents[3]


class DeterministicProductService:
    def __init__(self) -> None:
        self.requests: list[SummarizationRequest] = []

    async def summarize(
        self,
        request: SummarizationRequest,
    ) -> SummarizationResponse:
        self.requests.append(request)
        return SummarizationResponse(
            summary=f"deterministic summary: {request.text}",
            prompt="M4.1 test prompt",
            model=request.model,
            prompt_tokens=7,
            completion_tokens=3,
        )


def _build_application() -> tuple[
    SummarizationApplication,
    DeterministicProductService,
]:
    service = DeterministicProductService()
    pipeline = SummarizationPipeline(
        chunker=TextChunker(
            ChunkingConfig(max_tokens=500, overlap_tokens=0),
        ),
        selector=SummarizationStrategySelector(
            StrategySelectionConfig(
                direct_max_tokens=500,
                map_reduce_max_tokens=1_000,
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


def test_realistic_text_uses_canonical_application_product_flow(monkeypatch) -> None:
    application, service = _build_application()
    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": REALISTIC_TEXT,
            "provider": "fake",
            "model": "m4-1-demo",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": f"deterministic summary: {REALISTIC_TEXT}",
        "model": "m4-1-demo",
        "prompt_tokens": 7,
        "completion_tokens": 3,
        "total_tokens": 10,
    }
    assert len(service.requests) == 1
    assert service.requests[0].text == REALISTIC_TEXT


def test_legacy_frontend_is_explicitly_outside_the_canonical_v11_product_path():
    legacy_template = (
        ROOT / "app" / "legacy" / "v7.6" / "templates" / "index.html"
    ).read_text(encoding="utf-8")

    assert 'action="/summarize"' in legacy_template
    assert 'action="/api/v1/summarize"' not in legacy_template
    assert any(getattr(route, "path", None) == "/" for route in app.routes)
