from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.ai import router

from types import SimpleNamespace

import app.routes.ai as ai_routes

import asyncio
from concurrent.futures import ThreadPoolExecutor


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


def test_endpoint_preserves_concurrent_request_isolation(
    monkeypatch,
) -> None:
    class ConcurrentApplication:
        async def summarize(self, request):
            delays = {
                "model-slow": 0.03,
                "model-medium": 0.02,
                "model-fast": 0.01,
            }

            await asyncio.sleep(delays[request.model])

            prompt_tokens = {
                "model-slow": 11,
                "model-medium": 22,
                "model-fast": 33,
            }[request.model]

            completion_tokens = {
                "model-slow": 1,
                "model-medium": 2,
                "model-fast": 3,
            }[request.model]

            return SimpleNamespace(
                summary=f"summary:{request.text}",
                model=request.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                metadata=SimpleNamespace(
                    strategy="direct",
                    chunk_count=1,
                    intelligence_mode="preserve",
                    trace_id=f"trace:{request.model}",
                    explainability_summary="execution preserved",
                    attributes={
                        "intelligence_observability_status": "normal",
                        "intelligence_diagnostic_code": "INTELLIGENCE_NORMAL",
                        "intelligence_diagnostic_message": "normal execution",
                        "recovery_occurred": "false",
                        "recovery_action": "",
                        "recovery_strategy": "",
                    },
                ),
            )

    application = ConcurrentApplication()

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    app = FastAPI()
    app.include_router(router)

    def post_summary(text: str, model: str):
        with TestClient(app) as client:
            return client.post(
                "/api/v1/summarize",
                json={
                    "text": text,
                    "provider": "fake",
                    "model": model,
                },
            )

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(
                post_summary,
                "slow source",
                "model-slow",
            ),
            executor.submit(
                post_summary,
                "medium source",
                "model-medium",
            ),
            executor.submit(
                post_summary,
                "fast source",
                "model-fast",
            ),
        ]

        responses = [future.result() for future in futures]

    slow_response, medium_response, fast_response = responses

    assert slow_response.status_code == 200
    assert medium_response.status_code == 200
    assert fast_response.status_code == 200

    slow_body = slow_response.json()
    medium_body = medium_response.json()
    fast_body = fast_response.json()

    assert slow_body["summary"] == "summary:slow source"
    assert slow_body["model"] == "model-slow"
    assert slow_body["prompt_tokens"] == 11
    assert slow_body["completion_tokens"] == 1
    assert slow_body["total_tokens"] == 12

    assert medium_body["summary"] == "summary:medium source"
    assert medium_body["model"] == "model-medium"
    assert medium_body["prompt_tokens"] == 22
    assert medium_body["completion_tokens"] == 2
    assert medium_body["total_tokens"] == 24

    assert fast_body["summary"] == "summary:fast source"
    assert fast_body["model"] == "model-fast"
    assert fast_body["prompt_tokens"] == 33
    assert fast_body["completion_tokens"] == 3
    assert fast_body["total_tokens"] == 36

    assert slow_body["metadata"]["trace_id"] == "trace:model-slow"
    assert medium_body["metadata"]["trace_id"] == "trace:model-medium"
    assert fast_body["metadata"]["trace_id"] == "trace:model-fast"


def test_endpoint_isolates_failure_between_concurrent_requests(
    monkeypatch,
) -> None:
    class MixedOutcomeApplication:
        async def summarize(self, request):
            await asyncio.sleep(0)

            if request.text == "failing source":
                raise RuntimeError("isolated internal provider failure")

            return SimpleNamespace(
                summary=f"summary:{request.text}",
                model=request.model,
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
                metadata=SimpleNamespace(
                    strategy="direct",
                    chunk_count=1,
                    intelligence_mode="preserve",
                    trace_id=f"trace:{request.model}",
                    explainability_summary="execution preserved",
                    attributes={
                        "intelligence_observability_status": "normal",
                        "intelligence_diagnostic_code": "INTELLIGENCE_NORMAL",
                        "intelligence_diagnostic_message": "normal execution",
                        "recovery_occurred": "false",
                        "recovery_action": "",
                        "recovery_strategy": "",
                    },
                ),
            )

    application = MixedOutcomeApplication()

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    app = FastAPI()
    app.include_router(router)

    def post_summary(
        text: str,
        model: str,
    ):
        with TestClient(app) as client:
            return client.post(
                "/api/v1/summarize",
                json={
                    "text": text,
                    "provider": "fake",
                    "model": model,
                },
            )

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(
                post_summary,
                "first source",
                "model-one",
            ),
            executor.submit(
                post_summary,
                "failing source",
                "model-fail",
            ),
            executor.submit(
                post_summary,
                "third source",
                "model-three",
            ),
        ]

        first_response = futures[0].result()
        failed_response = futures[1].result()
        third_response = futures[2].result()

    assert first_response.status_code == 200
    assert failed_response.status_code == 500
    assert third_response.status_code == 200

    first_body = first_response.json()
    failed_body = failed_response.json()
    third_body = third_response.json()

    assert first_body["summary"] == "summary:first source"
    assert first_body["model"] == "model-one"

    assert failed_body["detail"]["error"]["code"] == "SUMMARIZATION_FAILED"
    assert (
        failed_body["detail"]["error"]["message"]
        == "summarization could not be completed"
    )

    assert "isolated internal provider failure" not in failed_response.text
    assert "RuntimeError" not in failed_response.text

    assert third_body["summary"] == "summary:third source"
    assert third_body["model"] == "model-three"

    assert first_body["metadata"]["trace_id"] == "trace:model-one"
    assert third_body["metadata"]["trace_id"] == "trace:model-three"


def test_endpoint_repeated_success_responses_remain_stable(
    monkeypatch,
) -> None:
    class StableApplication:
        async def summarize(self, request):
            return SimpleNamespace(
                summary=f"summary:{request.text}",
                model=request.model,
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
                metadata=SimpleNamespace(
                    strategy="direct",
                    chunk_count=1,
                    intelligence_mode="preserve",
                    trace_id=f"trace:{request.model}",
                    explainability_summary="execution preserved",
                    attributes={
                        "intelligence_observability_status": "normal",
                        "intelligence_diagnostic_code": "INTELLIGENCE_NORMAL",
                        "intelligence_diagnostic_message": "normal execution",
                        "recovery_occurred": "false",
                        "recovery_action": "",
                        "recovery_strategy": "",
                    },
                ),
            )

    application = StableApplication()

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as client:
        responses = [
            client.post(
                "/api/v1/summarize",
                json={
                    "text": "stable source",
                    "provider": "fake",
                    "model": "stable-model",
                },
            )
            for _ in range(5)
        ]

    assert all(response.status_code == 200 for response in responses)

    bodies = [response.json() for response in responses]

    assert all(body["summary"] == "summary:stable source" for body in bodies)

    assert all(body["model"] == "stable-model" for body in bodies)

    assert all(body["prompt_tokens"] == 10 for body in bodies)

    assert all(body["completion_tokens"] == 5 for body in bodies)

    assert all(body["total_tokens"] == 15 for body in bodies)

    assert all(body["metadata"]["strategy"] == "direct" for body in bodies)

    assert all(body["metadata"]["chunk_count"] == 1 for body in bodies)

    assert all(body["metadata"]["trace_id"] == "trace:stable-model" for body in bodies)

    assert all(body["metadata"]["recovery_occurred"] is False for body in bodies)

    assert all(body["metadata"]["recovery_action"] is None for body in bodies)

    assert all(body["metadata"]["recovery_strategy"] is None for body in bodies)


def test_endpoint_remains_usable_after_sequential_failure(
    monkeypatch,
) -> None:
    class SequentialMixedOutcomeApplication:
        async def summarize(self, request):
            if request.text == "failing source":
                raise RuntimeError("isolated internal provider failure")

            return SimpleNamespace(
                summary=f"summary:{request.text}",
                model=request.model,
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
                metadata=SimpleNamespace(
                    strategy="direct",
                    chunk_count=1,
                    intelligence_mode="preserve",
                    trace_id=f"trace:{request.model}",
                    explainability_summary="execution preserved",
                    attributes={
                        "intelligence_observability_status": "normal",
                        "intelligence_diagnostic_code": "INTELLIGENCE_NORMAL",
                        "intelligence_diagnostic_message": "normal execution",
                        "recovery_occurred": "false",
                        "recovery_action": "",
                        "recovery_strategy": "",
                    },
                ),
            )

    application = SequentialMixedOutcomeApplication()

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as client:
        first_response = client.post(
            "/api/v1/summarize",
            json={
                "text": "first source",
                "provider": "fake",
                "model": "model-one",
            },
        )

        failed_response = client.post(
            "/api/v1/summarize",
            json={
                "text": "failing source",
                "provider": "fake",
                "model": "model-fail",
            },
        )

        third_response = client.post(
            "/api/v1/summarize",
            json={
                "text": "third source",
                "provider": "fake",
                "model": "model-three",
            },
        )

    assert first_response.status_code == 200
    assert failed_response.status_code == 500
    assert third_response.status_code == 200

    first_body = first_response.json()
    failed_body = failed_response.json()
    third_body = third_response.json()

    assert first_body["summary"] == "summary:first source"
    assert first_body["model"] == "model-one"
    assert first_body["metadata"]["trace_id"] == "trace:model-one"

    assert failed_body["detail"]["error"]["code"] == "SUMMARIZATION_FAILED"
    assert (
        failed_body["detail"]["error"]["message"]
        == "summarization could not be completed"
    )

    assert "isolated internal provider failure" not in failed_response.text
    assert "RuntimeError" not in failed_response.text
    assert "recovery_occurred" not in failed_response.text
    assert "recovery_action" not in failed_response.text
    assert "recovery_strategy" not in failed_response.text

    assert third_body["summary"] == "summary:third source"
    assert third_body["model"] == "model-three"
    assert third_body["metadata"]["trace_id"] == "trace:model-three"

    assert third_body["prompt_tokens"] == 10
    assert third_body["completion_tokens"] == 5
    assert third_body["total_tokens"] == 15

    assert third_body["metadata"]["recovery_occurred"] is False
    assert third_body["metadata"]["recovery_action"] is None
    assert third_body["metadata"]["recovery_strategy"] is None


def test_endpoint_repeated_recovery_responses_remain_stable(
    monkeypatch,
) -> None:
    class RecoveringApplication:
        async def summarize(self, request):
            return SimpleNamespace(
                summary=f"recovered:{request.text}",
                model=request.model,
                prompt_tokens=20,
                completion_tokens=10,
                total_tokens=30,
                metadata=SimpleNamespace(
                    strategy="hierarchical",
                    chunk_count=4,
                    intelligence_mode="preserve",
                    trace_id=f"trace:{request.model}",
                    explainability_summary="execution preserved",
                    attributes={
                        "intelligence_observability_status": "normal",
                        "intelligence_diagnostic_code": "INTELLIGENCE_NORMAL",
                        "intelligence_diagnostic_message": "normal execution",
                        "recovery_occurred": "true",
                        "recovery_action": "fallback",
                        "recovery_strategy": "map_reduce",
                    },
                ),
            )

    application = RecoveringApplication()

    monkeypatch.setattr(
        ai_routes,
        "build_summarization_application",
        lambda: application,
    )

    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as client:
        responses = [
            client.post(
                "/api/v1/summarize",
                json={
                    "text": "recoverable source",
                    "provider": "fake",
                    "model": "recovery-model",
                },
            )
            for _ in range(5)
        ]

    assert all(response.status_code == 200 for response in responses)

    bodies = [response.json() for response in responses]

    assert all(body["summary"] == "recovered:recoverable source" for body in bodies)

    assert all(body["model"] == "recovery-model" for body in bodies)

    assert all(body["prompt_tokens"] == 20 for body in bodies)

    assert all(body["completion_tokens"] == 10 for body in bodies)

    assert all(body["total_tokens"] == 30 for body in bodies)

    assert all(body["metadata"]["strategy"] == "hierarchical" for body in bodies)

    assert all(body["metadata"]["chunk_count"] == 4 for body in bodies)

    assert all(
        body["metadata"]["trace_id"] == "trace:recovery-model" for body in bodies
    )

    assert all(body["metadata"]["recovery_occurred"] is True for body in bodies)

    assert all(body["metadata"]["recovery_action"] == "fallback" for body in bodies)

    assert all(body["metadata"]["recovery_strategy"] == "map_reduce" for body in bodies)

    assert all("RuntimeError" not in response.text for response in responses)

    assert all("FallbackDecision" not in response.text for response in responses)
