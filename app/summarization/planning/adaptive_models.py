"""
V9.3-M4 immutable adaptive strategy planning models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.summarization.strategies.models import SummarizationStrategyType


@dataclass(frozen=True)
class AdaptiveStrategyDecision:
    """Deterministic strategy decision derived from the V9.2 baseline."""

    baseline_strategy: SummarizationStrategyType
    selected_strategy: SummarizationStrategyType
    promoted: bool
    reasons: tuple[str, ...] = ()
    signals: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.baseline_strategy, SummarizationStrategyType):
            raise TypeError("baseline_strategy must be a SummarizationStrategyType")
        if not isinstance(self.selected_strategy, SummarizationStrategyType):
            raise TypeError("selected_strategy must be a SummarizationStrategyType")
        if self.selected_strategy is self.baseline_strategy and self.promoted:
            raise ValueError("promoted must be false when the strategy is unchanged")
        if self.selected_strategy is not self.baseline_strategy and not self.promoted:
            raise ValueError("promoted must be true when the strategy changes")
        if not self.reasons:
            raise ValueError("reasons must not be empty")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")


__all__ = ["AdaptiveStrategyDecision"]
