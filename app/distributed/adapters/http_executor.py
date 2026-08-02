"""
AI Summarizer V8.0

HTTP remote execution adapter.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from app.distributed.protocols import TaskEnvelope

from .execution_result import RemoteExecutionResult
from .executor_interface import RemoteExecutor


class HTTPExecutor(RemoteExecutor):
    """
    Executes tasks through HTTP runtime endpoint.
    """

    def __init__(
        self,
        endpoint: str,
        timeout: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:

        self._endpoint = endpoint

        self._timeout = timeout

        self._client = client

    async def execute(
        self,
        task: TaskEnvelope,
    ) -> RemoteExecutionResult:

        start = time.perf_counter()

        payload = {
            "task_id": task.task_id,
            "execution_id": task.execution_id,
            "node_id": task.node_id,
            "agent_type": task.agent_type,
        }

        client = self._client

        close_client = False

        if client is None:

            client = httpx.AsyncClient(timeout=self._timeout)

            close_client = True

        try:

            response = await client.post(
                self._endpoint,
                json=payload,
            )

            response.raise_for_status()

            data: dict[str, Any] = response.json()

            return RemoteExecutionResult(
                success=True,
                output=data.get("output"),
                worker_id=data.get("worker_id"),
                execution_time=(time.perf_counter() - start),
            )

        except Exception as exc:

            return RemoteExecutionResult(
                success=False,
                error=str(exc),
                execution_time=(time.perf_counter() - start),
            )

        finally:

            if close_client:

                await client.aclose()
