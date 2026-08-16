"""
V9.3-M6 models for deterministic summarization quality evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QualityMetricName(str, Enum):
    """Supported deterministic quality dimensions."""

    NON_EMPTY = "non_empty"
    COMPRESSION = "compression"
    COVERAGE = "coverage"
    REPETITION = "repetition"


@dataclass(frozen=True)
class QualityMetric:
    """
    Immutable result for one quality dimension.

    Scores are normalized to the range [0.0, 1.0].
    """

    name: QualityMetricName
    score: float
    rationale: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, QualityMetricName):
            raise TypeError("name must be a QualityMetricName")

        if not isinstance(self.score, (int, float)):
            raise TypeError("score must be numeric")

        if not 0.0 <= float(self.score) <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")

        if not isinstance(self.rationale, str):
            raise TypeError("rationale must be a string")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")


@dataclass(frozen=True)
class QualityEvaluation:
    """
    Immutable aggregate quality evaluation.

    The evaluator remains independent of any provider or LLM.
    """

    score: float
    passed: bool
    metrics: tuple[QualityMetric, ...]
    source_length: int
    summary_length: int
    evaluator_version: str = "v9.3-m6"
    threshold: float = 0.60
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.score, (int, float)):
            raise TypeError("score must be numeric")

        if not 0.0 <= float(self.score) <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")

        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a boolean")

        if not self.metrics:
            raise ValueError("metrics must not be empty")

        if self.source_length < 0:
            raise ValueError("source_length must be non-negative")

        if self.summary_length < 0:
            raise ValueError("summary_length must be non-negative")

        if not 0.0 <= float(self.threshold) <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")

        if not isinstance(self.evaluator_version, str):
            raise TypeError("evaluator_version must be a string")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")


__all__ = [
    "QualityEvaluation",
    "QualityMetric",
    "QualityMetricName",
]
