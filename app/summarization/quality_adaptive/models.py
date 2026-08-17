"""
V9.3-M7 immutable quality-aware execution models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.summarization.quality.models import QualityEvaluation
from app.summarization.strategies.models import SummarizationStrategyType


class AdaptiveExecutionAction(str, Enum):
    """Next execution action selected by the M7 layer."""

    ACCEPT = "accept"
    RETRY_CURRENT = "retry_current"
    ESCALATE_STRATEGY = "escalate_strategy"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class AdaptiveExecutionDecision:
    """
    Immutable quality-aware execution decision.

    The decision describes what the caller should do next. It does not
    execute a provider or mutate an existing execution contract.
    """

    action: AdaptiveExecutionAction
    current_strategy: SummarizationStrategyType
    next_strategy: SummarizationStrategyType | None
    quality: QualityEvaluation
    attempt: int
    max_attempts: int
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.action,
            AdaptiveExecutionAction,
        ):
            raise TypeError("action must be an AdaptiveExecutionAction")

        if not isinstance(
            self.current_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("current_strategy must be a " "SummarizationStrategyType")

        if self.next_strategy is not None and not isinstance(
            self.next_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError(
                "next_strategy must be a " "SummarizationStrategyType or None"
            )

        if not isinstance(
            self.quality,
            QualityEvaluation,
        ):
            raise TypeError("quality must be a QualityEvaluation")

        if not isinstance(self.attempt, int) or self.attempt < 1:
            raise ValueError("attempt must be a positive integer")

        if (
            not isinstance(
                self.max_attempts,
                int,
            )
            or self.max_attempts < 1
        ):
            raise ValueError("max_attempts must be a positive integer")

        if self.attempt > self.max_attempts:
            raise ValueError("attempt cannot exceed max_attempts")

        if not isinstance(self.reason, str) or not self.reason:
            raise ValueError("reason must not be empty")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")

        if self.action is AdaptiveExecutionAction.ACCEPT:
            if self.next_strategy is not None:
                raise ValueError("accept must not specify next_strategy")

        if self.action is AdaptiveExecutionAction.ESCALATE_STRATEGY:
            if self.next_strategy is None:
                raise ValueError("strategy escalation requires next_strategy")

        if self.action is AdaptiveExecutionAction.FALLBACK:
            if self.next_strategy is not None:
                raise ValueError("fallback must not specify next_strategy")


__all__ = [
    "AdaptiveExecutionAction",
    "AdaptiveExecutionDecision",
]
