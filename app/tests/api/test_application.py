"""Tests for the canonical V11 summarization application boundary."""

from __future__ import annotations

import pytest

from app.ai import (
    SummarizationRequest,
    SummarizationResponse,
)
from app.api.application import (
    SummarizationApplication,
    build_summarization_application,
)
from app.core.application_contracts import (
    SummarizationApplicationRequest,
)


class StubSummarizationService:
    def __init__(self) -> None:
        self.received_request: SummarizationRequest | None = None

    async def summarize(
        self,
        request: SummarizationRequest,
    ) -> SummarizationResponse:
        self.received_request = request

        return SummarizationResponse(
            summary="stub summary",
            prompt="stub prompt",
            model=request.model,
            prompt_tokens=10,
            completion_tokens=5,
        )


@pytest.mark.anyio
async def test_application_delegates_to_existing_service() -> None:
    service = StubSummarizationService()
    application = SummarizationApplication(service)  # type: ignore[arg-type]

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
async def test_application_translates_request_without_semantic_rewriting() -> None:
    service = StubSummarizationService()
    application = SummarizationApplication(service)  # type: ignore[arg-type]

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
    application = SummarizationApplication(service)  # type: ignore[arg-type]

    request = SummarizationApplicationRequest(
        text="Use the existing default prompt.",
        provider="fake",
        model="demo",
    )

    await application.summarize(request)

    assert service.received_request is not None
    assert service.received_request.prompt_name == "summary"
