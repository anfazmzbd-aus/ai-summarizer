"""
V9.3-M8 execution failure resilience boundary.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.summarization.strategies.models import (
    SummarizationStrategyType,
)

from .fallback import ResilienceFallbackPlanner
from .models import (
    FallbackDecision,
    ResilienceFailure,
)


class ResilientExecutionPlanner:
    """
    Convert an execution failure into a deterministic M8 recovery decision.

    This component does not execute a provider, retry an operation, or
    invoke a fallback strategy. It only translates the execution failure
    into the existing M8 resilience contract.
    """

    planner_version = "v9.3-m8"

    def __init__(
        self,
        *,
        max_attempts: int = 3,
    ) -> None:
        self._fallback_planner = ResilienceFallbackPlanner(
            max_attempts=max_attempts,
        )

    def decide_from_exception(
        self,
        *,
        strategy: SummarizationStrategyType,
        exception: BaseException,
        attempt: int = 1,
        attempted_strategies: Iterable[SummarizationStrategyType] = (),
        retryable: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> FallbackDecision:
        """
        Convert an execution exception into an M8 fallback decision.

        The exception itself is not raised, swallowed, or executed here.
        Its type and message are preserved in ResilienceFailure.
        """

        if not isinstance(
            strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("strategy must be a SummarizationStrategyType")

        if not isinstance(
            exception,
            BaseException,
        ):
            raise TypeError("exception must be a BaseException")

        if not isinstance(attempt, int):
            raise TypeError("attempt must be an integer")

        if attempt < 1:
            raise ValueError("attempt must be positive")

        if not isinstance(retryable, bool):
            raise TypeError("retryable must be a boolean")

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise TypeError("metadata must be a dictionary")

        failure = ResilienceFailure(
            error_type=type(exception).__name__,
            message=str(exception),
            strategy=strategy,
            attempt=attempt,
            retryable=retryable,
            metadata={
                **(metadata or {}),
                "planner_version": self.planner_version,
            },
        )

        return self._fallback_planner.decide(
            failure=failure,
            attempted_strategies=attempted_strategies,
        )


__all__ = [
    "ResilientExecutionPlanner",
]
