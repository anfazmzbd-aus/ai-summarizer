"""
AI Summarizer V9.1

Live integration tests for the /api/v1/summarize endpoint.

These tests are intentionally environment-gated.

Required environment variables:
    OPENROUTER_API_KEY

Optional:
    OPENROUTER_MODEL
    OPENROUTER_BASE_URL

The tests are skipped when OPENROUTER_API_KEY is unavailable so the
normal CI suite remains deterministic and credential-free.
"""

from __future__ import annotations

import os
import time
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient

from app.main import app

# from app.providers.config import ProviderType
from app.providers.factory import ProviderFactory
from app.providers.runtime import ProviderRuntime
from app.services.summarize_service import SummarizeService

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-5-mini",
)
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not OPENROUTER_API_KEY,
        reason="OPENROUTER_API_KEY is not configured",
    ),
]


def _build_live_service() -> SummarizeService:
    """
    Build SummarizeService using the OpenRouter OpenAI-compatible endpoint.

    The existing V9 provider abstraction remains unchanged. OpenRouter is
    selected through the OpenAI-compatible provider configuration.
    """

    factory = ProviderFactory()

    runtime = ProviderRuntime.openai(
        factory,
        api_key=OPENROUTER_API_KEY,
        model=OPENROUTER_MODEL,
        endpoint=OPENROUTER_BASE_URL,
    )

    return SummarizeService(
        llm_service=runtime.service,
        model=OPENROUTER_MODEL,
    )


def _assert_execution_response(body: dict) -> None:
    """Validate the public ExecutionResponse contract."""

    assert body["execution_id"]
    assert body["status"] == "success"

    assert isinstance(body["result"], dict)
    assert isinstance(body["node_outputs"], dict)
    assert isinstance(body["trace"], list)
    assert isinstance(body["metrics"], dict)
    assert isinstance(body["errors"], list)
    assert isinstance(body["metadata"], dict)

    assert body["result"].get("summary")


def test_live_summarize_service_openrouter_execution():
    """Validate live provider execution through SummarizeService."""

    service = _build_live_service()

    result = service.run(
        "Revenue increased by 25 percent during the latest quarter. "
        "The increase was driven by stronger enterprise demand."
    )

    body = result.model_dump()

    _assert_execution_response(body)

    assert body["result"]["summary"]
    assert body["metadata"]["execution_model"] == "deterministic_dag"


def test_live_summarize_service_openrouter_usage():
    """Validate token usage returned by the live provider."""

    service = _build_live_service()

    result = service.run(
        "The production deployment completed successfully. "
        "All critical services are operational."
    )

    body = result.model_dump()

    _assert_execution_response(body)

    metadata = body["result"]

    assert isinstance(metadata, dict)
    assert metadata["summary"]


def test_live_summarize_endpoint_openrouter():
    """
    Validate the public /summarize HTTP endpoint.

    The endpoint itself currently constructs its default service, so this
    test verifies the public contract independently from the direct service
    composition test above.
    """

    client = TestClient(app)

    response = client.post(
        "/summarize",
        json={
            "text": (
                "Revenue increased by 25 percent during the latest quarter. "
                "Enterprise demand was the primary driver."
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    _assert_execution_response(body)


def test_live_summarize_service_latency():
    """Validate that live execution records a positive latency."""

    service = _build_live_service()

    start = time.perf_counter()

    result = service.run(
        "The company completed its quarterly operational review "
        "and identified several opportunities for improvement."
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    body = result.model_dump()

    _assert_execution_response(body)

    assert elapsed_ms > 0

    metrics = body["metrics"]

    assert isinstance(metrics, dict)
