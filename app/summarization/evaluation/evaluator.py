"""
V9.3-M10 deterministic production evaluation.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .models import (
    EvaluationDimension,
    EvaluationResult,
)


class SummarizationEvaluationEvaluator:
    """
    Evaluate the structural integrity of a V9.3 execution record.

    This evaluator is deliberately provider-independent.

    It verifies the presence and validity of outputs from existing
    intelligence layers. It does not execute or mutate those layers.
    """

    evaluator_version = "v9.3-m10"

    _DIMENSIONS = (
        EvaluationDimension.PLANNING,
        EvaluationDimension.CONSTRAINTS,
        EvaluationDimension.QUALITY,
        EvaluationDimension.RESILIENCE,
        EvaluationDimension.STREAMING,
    )

    def evaluate(
        self,
        *,
        planning: Mapping[str, Any] | None = None,
        constraints: Mapping[str, Any] | None = None,
        quality: Mapping[str, Any] | None = None,
        resilience: Mapping[str, Any] | None = None,
        streaming: Mapping[str, Any] | None = None,
    ) -> EvaluationResult:
        """
        Evaluate a deterministic V9.3 execution record.

        Each supplied mapping represents an already-computed result
        from an existing V9.3 layer.
        """

        records = {
            EvaluationDimension.PLANNING: planning,
            EvaluationDimension.CONSTRAINTS: constraints,
            EvaluationDimension.QUALITY: quality,
            EvaluationDimension.RESILIENCE: resilience,
            EvaluationDimension.STREAMING: streaming,
        }

        for dimension, record in records.items():
            if record is not None and not isinstance(
                record,
                Mapping,
            ):
                raise TypeError(f"{dimension.value} must be a mapping or None")

        dimensions = {
            dimension: self._evaluate_dimension(
                dimension,
                record,
            )
            for dimension, record in records.items()
        }

        passed_dimensions = sum(value for value in dimensions.values())

        score = passed_dimensions / len(dimensions) if dimensions else 0.0

        failures = tuple(
            dimension.value for dimension, passed in dimensions.items() if not passed
        )

        passed = all(dimensions.values())

        return EvaluationResult(
            passed=passed,
            dimensions=dimensions,
            score=score,
            failures=failures,
            metadata={
                "evaluator_version": self.evaluator_version,
                "deterministic": True,
                "dimension_count": len(dimensions),
            },
        )

    @staticmethod
    def _evaluate_dimension(
        dimension: EvaluationDimension,
        record: Mapping[str, Any] | None,
    ) -> bool:
        if record is None:
            return False

        if dimension is EvaluationDimension.PLANNING:
            return bool(
                record.get("strategy")
                and (record.get("planner_version") or record.get("plan"))
            )

        if dimension is EvaluationDimension.CONSTRAINTS:
            return bool(
                record.get("token_budget") is not None
                or record.get("latency_budget") is not None
                or record.get("cost_budget") is not None
            )

        if dimension is EvaluationDimension.QUALITY:
            score = record.get("score")

            return isinstance(score, (int, float)) and 0.0 <= float(score) <= 1.0

        if dimension is EvaluationDimension.RESILIENCE:
            return "action" in record or "fallback_used" in record

        if dimension is EvaluationDimension.STREAMING:
            return bool(
                record.get("intelligent")
                or record.get("intelligence")
                or record.get("streamer_version")
            )

        return False


__all__ = [
    "SummarizationEvaluationEvaluator",
]
