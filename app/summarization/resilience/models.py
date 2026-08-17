"""
V9.3-M8 immutable resilience models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.summarization.strategies.models import (
    SummarizationStrategyType,
)


class FallbackAction(str, Enum):
    """Next action selected after an execution failure."""

    FALLBACK = "fallback"
    RETRY = "retry"
    TERMINATE = "terminate"


@dataclass(frozen=True)
class ResilienceFailure:
    """
    Immutable normalized representation of an execution failure.

    The original exception is preserved separately from the normalized
    failure metadata so callers retain the original error provenance.
    """

    error_type: str
    message: str
    strategy: SummarizationStrategyType
    attempt: int
    retryable: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.error_type, str) or not self.error_type:
            raise ValueError("error_type must not be empty")

        if not isinstance(self.message, str):
            raise TypeError("message must be a string")

        if not isinstance(
            self.strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("strategy must be a SummarizationStrategyType")

        if not isinstance(self.attempt, int):
            raise TypeError("attempt must be an integer")

        if self.attempt < 1:
            raise ValueError("attempt must be positive")

        if not isinstance(self.retryable, bool):
            raise TypeError("retryable must be a boolean")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")


@dataclass(frozen=True)
class FallbackDecision:
    """
    Immutable resilience decision.

    This object describes the recovery action. It does not execute the
    fallback strategy.
    """

    action: FallbackAction
    failed_strategy: SummarizationStrategyType
    fallback_strategy: SummarizationStrategyType | None
    failure: ResilienceFailure
    attempted_strategies: tuple[SummarizationStrategyType, ...]
    max_attempts: int
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.action,
            FallbackAction,
        ):
            raise TypeError("action must be a FallbackAction")

        if not isinstance(
            self.failed_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("failed_strategy must be a " "SummarizationStrategyType")

        if self.fallback_strategy is not None and not isinstance(
            self.fallback_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError(
                "fallback_strategy must be a " "SummarizationStrategyType or None"
            )

        if not isinstance(
            self.failure,
            ResilienceFailure,
        ):
            raise TypeError("failure must be a ResilienceFailure")

        if not self.attempted_strategies:
            raise ValueError("attempted_strategies must not be empty")

        if not all(
            isinstance(
                strategy,
                SummarizationStrategyType,
            )
            for strategy in self.attempted_strategies
        ):
            raise TypeError(
                "attempted_strategies must contain only "
                "SummarizationStrategyType values"
            )

        if self.failed_strategy not in self.attempted_strategies:
            raise ValueError(
                "failed_strategy must be present in " "attempted_strategies"
            )

        if not isinstance(self.max_attempts, int):
            raise TypeError("max_attempts must be an integer")

        if self.max_attempts < 1:
            raise ValueError("max_attempts must be positive")

        if not isinstance(self.reason, str) or not self.reason:
            raise ValueError("reason must not be empty")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")

        if self.action is FallbackAction.FALLBACK:
            if self.fallback_strategy is None:
                raise ValueError("fallback action requires fallback_strategy")

        if self.action is FallbackAction.TERMINATE:
            if self.fallback_strategy is not None:
                raise ValueError("terminate action cannot specify " "fallback_strategy")

        if self.action is FallbackAction.RETRY:
            if self.fallback_strategy is not None:
                raise ValueError("retry action cannot specify " "fallback_strategy")


__all__ = [
    "FallbackAction",
    "FallbackDecision",
    "ResilienceFailure",
]
