"""
V9.3-M10 deterministic evaluation models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvaluationDimension(str, Enum):
    """Dimensions evaluated by the M10 production evaluator."""

    PLANNING = "planning"
    CONSTRAINTS = "constraints"
    QUALITY = "quality"
    RESILIENCE = "resilience"
    STREAMING = "streaming"


@dataclass(frozen=True)
class EvaluationResult:
    """
    Immutable production-evaluation result.

    The result records whether each V9.3 intelligence dimension is
    internally coherent. It does not execute providers or alter any
    existing orchestration decision.
    """

    passed: bool
    dimensions: dict[EvaluationDimension, bool]
    score: float
    failures: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a boolean")

        if not isinstance(self.dimensions, dict):
            raise TypeError("dimensions must be a dictionary")

        for dimension, value in self.dimensions.items():
            if not isinstance(
                dimension,
                EvaluationDimension,
            ):
                raise TypeError("dimension keys must be EvaluationDimension values")

            if not isinstance(value, bool):
                raise TypeError("dimension values must be boolean")

        if not isinstance(self.score, (int, float)):
            raise TypeError("score must be numeric")

        if not 0.0 <= float(self.score) <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")

        if not isinstance(self.failures, tuple):
            raise TypeError("failures must be a tuple")

        if not all(isinstance(failure, str) and failure for failure in self.failures):
            raise ValueError("failures must contain non-empty strings")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")

        expected_passed = all(self.dimensions.values()) if self.dimensions else False

        if self.passed != expected_passed:
            raise ValueError("passed must match the dimension results")

        expected_failures = tuple(
            dimension.value
            for dimension, passed in self.dimensions.items()
            if not passed
        )

        if self.failures != expected_failures:
            raise ValueError("failures must match failed dimensions")


__all__ = [
    "EvaluationDimension",
    "EvaluationResult",
]
