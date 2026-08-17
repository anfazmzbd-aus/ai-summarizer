"""
V9.3-M8 deterministic resilience and fallback planning.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.summarization.strategies.models import (
    SummarizationStrategyType,
)

from .models import (
    FallbackAction,
    FallbackDecision,
    ResilienceFailure,
)


class ResilienceFallbackPlanner:
    """
    Determine the next safe recovery action after execution failure.

    The planner is deterministic and provider-independent.

    It does not execute providers, strategies, retries, or fallbacks.
    """

    planner_version = "v9.3-m8"

    _FALLBACK_ORDER = (
        SummarizationStrategyType.HIERARCHICAL,
        SummarizationStrategyType.MAP_REDUCE,
        SummarizationStrategyType.DIRECT,
    )

    def __init__(
        self,
        *,
        max_attempts: int = 3,
    ) -> None:
        if not isinstance(max_attempts, int):
            raise TypeError("max_attempts must be an integer")

        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")

        self.max_attempts = max_attempts

    def decide(
        self,
        *,
        failure: ResilienceFailure,
        attempted_strategies: Iterable[SummarizationStrategyType],
    ) -> FallbackDecision:
        """
        Determine the next resilience action.

        Fallbacks are selected from the deterministic strategy chain.
        Already-attempted strategies are never selected again.
        """

        if not isinstance(
            failure,
            ResilienceFailure,
        ):
            raise TypeError("failure must be a ResilienceFailure")

        attempted = self._normalize_attempts(attempted_strategies)

        if failure.strategy not in attempted:
            attempted = (
                *attempted,
                failure.strategy,
            )

        next_strategy = self._next_available(
            failure.strategy,
            attempted,
        )

        if next_strategy is not None:
            return FallbackDecision(
                action=FallbackAction.FALLBACK,
                failed_strategy=failure.strategy,
                fallback_strategy=next_strategy,
                failure=failure,
                attempted_strategies=attempted,
                max_attempts=self.max_attempts,
                reason=(
                    "execution failed; selecting the next "
                    "unattempted fallback strategy"
                ),
                metadata={
                    "planner_version": self.planner_version,
                    "fallback": True,
                    "attempt_count": len(attempted),
                    "original_error_type": failure.error_type,
                },
            )

        if failure.retryable and failure.attempt < self.max_attempts:
            return FallbackDecision(
                action=FallbackAction.RETRY,
                failed_strategy=failure.strategy,
                fallback_strategy=None,
                failure=failure,
                attempted_strategies=attempted,
                max_attempts=self.max_attempts,
                reason=(
                    "no unattempted fallback strategy remains; "
                    "retry budget is still available"
                ),
                metadata={
                    "planner_version": self.planner_version,
                    "fallback": False,
                    "attempt_count": len(attempted),
                    "original_error_type": failure.error_type,
                },
            )

        return FallbackDecision(
            action=FallbackAction.TERMINATE,
            failed_strategy=failure.strategy,
            fallback_strategy=None,
            failure=failure,
            attempted_strategies=attempted,
            max_attempts=self.max_attempts,
            reason=("execution failed and no further recovery " "action is permitted"),
            metadata={
                "planner_version": self.planner_version,
                "fallback": False,
                "attempt_count": len(attempted),
                "original_error_type": failure.error_type,
            },
        )

    @staticmethod
    def _normalize_attempts(
        attempted_strategies: Iterable[SummarizationStrategyType],
    ) -> tuple[SummarizationStrategyType, ...]:
        if isinstance(
            attempted_strategies,
            (str, bytes),
        ):
            raise TypeError(
                "attempted_strategies must be an iterable "
                "of SummarizationStrategyType"
            )

        result: list[SummarizationStrategyType] = []

        for strategy in attempted_strategies:
            if not isinstance(
                strategy,
                SummarizationStrategyType,
            ):
                raise TypeError(
                    "attempted_strategies must contain only "
                    "SummarizationStrategyType values"
                )

            if strategy not in result:
                result.append(strategy)

        return tuple(result)

    def _next_available(
        self,
        failed_strategy: SummarizationStrategyType,
        attempted: tuple[
            SummarizationStrategyType,
            ...,
        ],
    ) -> SummarizationStrategyType | None:
        try:
            index = self._FALLBACK_ORDER.index(failed_strategy)
        except ValueError:
            return None

        # Only strategies after the failed strategy are considered
        # fallbacks. This makes the chain deterministic and prevents
        # oscillation.
        candidates = self._FALLBACK_ORDER[index + 1 :]

        for strategy in candidates:
            if strategy not in attempted:
                return strategy

        return None


__all__ = [
    "ResilienceFallbackPlanner",
]
