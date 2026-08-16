"""
V9.3-M5 deterministic cost, token, and latency planning models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.summarization.strategies.models import SummarizationStrategyType


@dataclass(frozen=True)
class StrategyOptimizationEstimate:
    """Deterministic resource estimate for a summarization strategy."""

    strategy: SummarizationStrategyType
    input_tokens: int
    chunk_count: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_total_tokens: int
    estimated_latency_ms: int
    estimated_cost_units: int
    rationale: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "input_tokens",
            "chunk_count",
            "estimated_input_tokens",
            "estimated_output_tokens",
            "estimated_total_tokens",
            "estimated_latency_ms",
            "estimated_cost_units",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")

        if not isinstance(
            self.strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("strategy must be a SummarizationStrategyType")

        if not isinstance(self.rationale, tuple):
            raise TypeError("rationale must be a tuple")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")


@dataclass(frozen=True)
class StrategyOptimizationDecision:
    """Deterministic optimization decision over an existing strategy."""

    baseline_strategy: SummarizationStrategyType
    selected_strategy: SummarizationStrategyType
    estimates: tuple[StrategyOptimizationEstimate, ...]
    reason: str
    constrained: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.baseline_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("baseline_strategy must be a SummarizationStrategyType")

        if not isinstance(
            self.selected_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("selected_strategy must be a SummarizationStrategyType")

        if not self.estimates:
            raise ValueError("estimates must not be empty")

        if not isinstance(self.reason, str) or not self.reason:
            raise ValueError("reason must not be empty")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")
