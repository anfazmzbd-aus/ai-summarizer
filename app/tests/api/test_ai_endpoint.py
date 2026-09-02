from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.ai import router

from types import SimpleNamespace

import app.routes.ai as ai_routes


def test_endpoint():

    app = FastAPI()

    app.include_router(router)

    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Hello World",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "summary" in body
    assert body["model"] == "demo"


def test_endpoint_projects_product_safe_recovery_metadata(
    monkeypatch,
) -> None:
    class StubApplication:
        async def summarize(self, request):
            return SimpleNamespace(
                summary="recovered summary",
                model="demo",
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
                metadata=SimpleNamespace(
                    strategy="hierarchical",
                    chunk_count=4,
                    intelligence_mode="preserve",
                    trace_id="trace-id",
                    explainability_summary="execution preserved",
                    attributes={
                        "intelligence_observability_status": "normal",
                        "intelligence_diagnostic_code": ("INTELLIGENCE_NORMAL"),
                        "intelligence_diagnostic_message": ("normal execution"),
                        "recovery_occurred": "true",
                        "recovery_action": "fallback",
                        "recovery_strategy": "map_reduce",
                    },
                ),
            )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: StubApplication(),
    )

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "long source text",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["metadata"]["strategy"] == "hierarchical"
    assert body["metadata"]["recovery_occurred"] is True
    assert body["metadata"]["recovery_action"] == "fallback"
    assert body["metadata"]["recovery_strategy"] == "map_reduce"

    serialized = response.text

    assert "FallbackDecision" not in serialized
    assert "RuntimeError" not in serialized
    assert "internal hierarchical failure" not in serialized


def test_endpoint_returns_product_safe_error_for_terminal_execution_failure(
    monkeypatch,
) -> None:
    class FailingApplication:
        async def summarize(self, request):
            raise RuntimeError(
                "summarization strategy execution terminated without a result"
            )

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: FailingApplication(),
    )

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "source text",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 500

    body = response.json()

    assert body["detail"]["error"]["code"] == "SUMMARIZATION_FAILED"
    assert body["detail"]["error"]["message"] == "summarization could not be completed"

    serialized = response.text

    assert "terminated without a result" not in serialized
    assert "RuntimeError" not in serialized
    assert "FallbackDecision" not in serialized


def test_endpoint_returns_product_safe_error_for_provider_failure(
    monkeypatch,
) -> None:
    application_calls = 0

    class FailingApplication:
        async def summarize(self, request):
            nonlocal application_calls
            application_calls += 1

            raise RuntimeError("openai upstream provider connection failed")

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: FailingApplication(),
    )

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "source text",
            "provider": "openai",
            "model": "demo",
        },
    )

    assert response.status_code == 500
    assert application_calls == 1

    body = response.json()

    assert body["detail"]["error"]["code"] == "SUMMARIZATION_FAILED"
    assert body["detail"]["error"]["message"] == "summarization could not be completed"

    serialized = response.text

    assert "openai upstream provider connection failed" not in serialized
    assert "RuntimeError" not in serialized
    assert "recovery_occurred" not in serialized
    assert "recovery_action" not in serialized
    assert "recovery_strategy" not in serialized


def test_endpoint_returns_product_safe_error_for_provider_timeout(
    monkeypatch,
) -> None:
    application_calls = 0

    class TimeoutApplication:
        async def summarize(self, request):
            nonlocal application_calls
            application_calls += 1

            raise TimeoutError("upstream provider timed out after 30 seconds")

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: TimeoutApplication(),
    )

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "source text",
            "provider": "openai",
            "model": "demo",
        },
    )

    assert response.status_code == 500
    assert application_calls == 1

    body = response.json()

    assert body["detail"]["error"]["code"] == "SUMMARIZATION_FAILED"
    assert body["detail"]["error"]["message"] == "summarization could not be completed"

    serialized = response.text

    assert "upstream provider timed out after 30 seconds" not in serialized
    assert "TimeoutError" not in serialized
    assert "recovery_occurred" not in serialized
    assert "recovery_action" not in serialized
    assert "recovery_strategy" not in serialized
