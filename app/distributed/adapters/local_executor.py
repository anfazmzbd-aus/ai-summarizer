"""
Local executor adapter.

Bridges the distributed runtime
to the existing V7.9 ExecutionEngine.
"""

from __future__ import annotations

import time

from app.distributed.protocols import TaskEnvelope

from .execution_result import RemoteExecutionResult
from .executor_interface import RemoteExecutor


class LocalExecutor(RemoteExecutor):

    def __init__(
        self,
        execution_engine,
    ) -> None:

        self._engine = execution_engine

    async def execute(
        self,
        task: TaskEnvelope,
    ) -> RemoteExecutionResult:

        start = time.perf_counter()

        result = await self._engine.execute(task)

        elapsed = time.perf_counter() - start

        return RemoteExecutionResult(
            success=True,
            output=result,
            execution_time=elapsed,
        )
