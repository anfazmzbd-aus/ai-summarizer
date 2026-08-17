"""
V9.3-M7 deterministic quality-aware adaptive execution planner.
"""

from __future__ import annotations

from app.summarization.quality.models import QualityEvaluation
from app.summarization.strategies.models import SummarizationStrategyType

from .models import (
    AdaptiveExecutionAction,
    AdaptiveExecutionDecision,
)


class QualityAwareAdaptiveExecutor:
    """
    Convert quality evaluation into a bounded next-execution decision.

    This class deliberately does not execute an LLM/provider. It returns
    the next action for the existing execution layer.
    """

    executor_version = "v9.3-m7"

    _STRATEGY_ORDER = (
        SummarizationStrategyType.DIRECT,
        SummarizationStrategyType.MAP_REDUCE,
        SummarizationStrategyType.HIERARCHICAL,
    )

    def __init__(
        self,
        *,
        max_attempts: int = 2,
        retry_threshold: float = 0.45,
    ) -> None:
        if not isinstance(max_attempts, int):
            raise TypeError("max_attempts must be an integer")

        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        if not isinstance(
            retry_threshold,
            (int, float),
        ):
            raise TypeError("retry_threshold must be numeric")

        if not 0.0 <= float(retry_threshold) <= 1.0:
            raise ValueError("retry_threshold must be between 0.0 and 1.0")

        self.max_attempts = max_attempts
        self.retry_threshold = float(retry_threshold)

    def decide(
        self,
        *,
        current_strategy: SummarizationStrategyType,
        quality: QualityEvaluation,
        attempt: int = 1,
    ) -> AdaptiveExecutionDecision:
        """
        Determine the next permitted execution action.

        A passing quality evaluation always terminates adaptation.

        A failing evaluation is handled in this order:

        1. escalate to the next strategy when available
        2. retry the current strategy when escalation is unavailable
        3. fallback when the attempt budget is exhausted
        """

        if not isinstance(
            current_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("current_strategy must be a " "SummarizationStrategyType")

        if not isinstance(
            quality,
            QualityEvaluation,
        ):
            raise TypeError("quality must be a QualityEvaluation")

        if not isinstance(attempt, int):
            raise TypeError("attempt must be an integer")

        if attempt < 1:
            raise ValueError("attempt must be at least 1")

        if attempt > self.max_attempts:
            raise ValueError("attempt cannot exceed max_attempts")

        if quality.passed:
            return self._decision(
                action=AdaptiveExecutionAction.ACCEPT,
                current_strategy=current_strategy,
                next_strategy=None,
                quality=quality,
                attempt=attempt,
                reason="quality threshold satisfied",
            )

        next_strategy = self._next_strategy(current_strategy)

        if next_strategy is not None:
            return self._decision(
                action=AdaptiveExecutionAction.ESCALATE_STRATEGY,
                current_strategy=current_strategy,
                next_strategy=next_strategy,
                quality=quality,
                attempt=attempt,
                reason=("quality threshold not satisfied; " "escalating strategy"),
            )

        if quality.score <= self.retry_threshold and attempt < self.max_attempts:
            return self._decision(
                action=AdaptiveExecutionAction.RETRY_CURRENT,
                current_strategy=current_strategy,
                next_strategy=None,
                quality=quality,
                attempt=attempt,
                reason=(
                    "quality is below retry threshold; " "retrying current strategy"
                ),
            )

        return self._decision(
            action=AdaptiveExecutionAction.FALLBACK,
            current_strategy=current_strategy,
            next_strategy=None,
            quality=quality,
            attempt=attempt,
            reason=(
                "quality remains below threshold and "
                "no further adaptive action is permitted"
            ),
        )

    def _decision(
        self,
        *,
        action: AdaptiveExecutionAction,
        current_strategy: SummarizationStrategyType,
        next_strategy: SummarizationStrategyType | None,
        quality: QualityEvaluation,
        attempt: int,
        reason: str,
    ) -> AdaptiveExecutionDecision:
        return AdaptiveExecutionDecision(
            action=action,
            current_strategy=current_strategy,
            next_strategy=next_strategy,
            quality=quality,
            attempt=attempt,
            max_attempts=self.max_attempts,
            reason=reason,
            metadata={
                "executor_version": self.executor_version,
                "quality_score": quality.score,
                "quality_threshold": quality.threshold,
                "retry_threshold": self.retry_threshold,
                "adaptive": True,
            },
        )

    def _next_strategy(
        self,
        current: SummarizationStrategyType,
    ) -> SummarizationStrategyType | None:
        index = self._STRATEGY_ORDER.index(current)

        if index + 1 >= len(self._STRATEGY_ORDER):
            return None

        return self._STRATEGY_ORDER[index + 1]


__all__ = [
    "QualityAwareAdaptiveExecutor",
]
