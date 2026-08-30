"""V11 M4.3 deterministic short, medium, and long product scenarios."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient
import pytest

import app.routes.ai as ai_routes
from app.ai import SummarizationRequest, SummarizationResponse
from app.api.application import SummarizationApplication
from app.core.application_contracts import (
    SummarizationApplicationRequest,
    SummarizationApplicationResult,
)
from app.core.summarization_pipeline_adapter import (
    AsyncSummarizationPipelineAdapter,
)
from app.main import app
from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.pipeline import SummarizationPipeline


_PROSE_BLOCK = (
    "The community energy team reviews household usage each month and shares "
    "practical ways to reduce waste without reducing comfort. Residents compare "
    "seasonal patterns, repair older equipment, and coordinate neighborhood "
    "projects that make renewable power easier to access. The team records each "
    "lesson so that new volunteers can build on tested improvements."
)


def _repeated_prose(repetitions: int) -> str:
    return "\n\n".join(
        f"Section {index + 1}: {_PROSE_BLOCK}" for index in range(repetitions)
    )


SHORT_TEXT = _repeated_prose(2)
MEDIUM_TEXT = _repeated_prose(70)
LONG_TEXT = _repeated_prose(240)


@dataclass(frozen=True)
class Scenario:
    name: str
    text: str
    expected_strategy: str


SCENARIOS = (
    Scenario("short", SHORT_TEXT, "direct"),
    Scenario("medium", MEDIUM_TEXT, "map_reduce"),
    Scenario("long", LONG_TEXT, "hierarchical"),
)


class DeterministicScenarioService:
    def __init__(self) -> None:
        self.requests: list[SummarizationRequest] = []

    async def summarize(
        self,
        request: SummarizationRequest,
    ) -> SummarizationResponse:
        self.requests.append(request)
        return SummarizationResponse(
            summary=f"scenario summary: {request.text}",
            prompt="M4.3 deterministic prompt",
            model=request.model,
            prompt_tokens=5,
            completion_tokens=2,
        )


class RecordingApplication(SummarizationApplication):
    def __init__(self, service: DeterministicScenarioService) -> None:
        super().__init__(
            service,  # type: ignore[arg-type]
            AsyncSummarizationPipelineAdapter(
                SummarizationPipeline(chunker=TextChunker())
            ),
        )
        self.last_result: SummarizationApplicationResult | None = None

    async def summarize(
        self,
        request: SummarizationApplicationRequest,
    ) -> SummarizationApplicationResult:
        result = await super().summarize(request)
        self.last_result = result
        return result


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda item: item.name)
def test_real_text_scenarios_use_canonical_api_and_existing_v9_strategy(
    monkeypatch,
    scenario: Scenario,
) -> None:
    service = DeterministicScenarioService()
    application = RecordingApplication(service)
    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    response = TestClient(app).post(
        "/api/v1/summarize",
        json={
            "text": scenario.text,
            "provider": "fake",
            "model": "m4-3-demo",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]
    assert body["summary"].startswith("scenario summary:")
    assert body["model"] == "m4-3-demo"
    assert body["prompt_tokens"] == len(service.requests) * 5
    assert body["completion_tokens"] == len(service.requests) * 2
    assert body["total_tokens"] == len(service.requests) * 7

    assert application.last_result is not None
    metadata = application.last_result.metadata
    assert metadata.strategy == scenario.expected_strategy
    assert metadata.chunk_count is not None
    assert metadata.chunk_count >= 1
    if scenario.name == "short":
        assert len(service.requests) == 1
    else:
        assert len(service.requests) > 1

    for request in service.requests:
        assert request.provider == "fake"
        assert request.model == "m4-3-demo"
