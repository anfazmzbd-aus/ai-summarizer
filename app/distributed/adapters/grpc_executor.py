"""
AI Summarizer V8.0

gRPC remote execution adapter.
"""

from __future__ import annotations

import time
from typing import Protocol

from app.distributed.protocols import TaskEnvelope

from .execution_result import RemoteExecutionResult
from .executor_interface import RemoteExecutor


class GRPCClient(Protocol):
    """
    gRPC client contract.

    Actual implementation can be:
    - grpc.aio client
    - generated protobuf client
    - custom transport
    """

    async def execute(
        self,
        payload: dict,
    ) -> dict: ...


class GRPCExecutor(RemoteExecutor):
    """
    Executes tasks using gRPC transport.
    """

    def __init__(
        self,
        client: GRPCClient,
    ) -> None:

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

        try:

            response = await self._client.execute(payload)

            return RemoteExecutionResult(
                success=True,
                output=response.get("output"),
                worker_id=response.get("worker_id"),
                execution_time=(time.perf_counter() - start),
            )

        except Exception as exc:

            return RemoteExecutionResult(
                success=False,
                error=str(exc),
                execution_time=(time.perf_counter() - start),
            )
