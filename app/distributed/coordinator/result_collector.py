"""
AI Summarizer V8.0 Distributed Runtime

Execution result collection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ExecutionResult:

    task_id: str

    success: bool

    output: Any = None

    error: str | None = None


class ResultCollector:
    """
    Collects worker execution results.
    """

    def __init__(self) -> None:

        self._results: dict[str, ExecutionResult] = {}

    def add(
        self,
        result: ExecutionResult,
    ) -> None:

        self._results[result.task_id] = result

    def get(
        self,
        task_id: str,
    ) -> ExecutionResult | None:

        return self._results.get(task_id)

    def count(self) -> int:

        return len(self._results)

    def all(
        self,
    ) -> list[ExecutionResult]:

        return list(self._results.values())
