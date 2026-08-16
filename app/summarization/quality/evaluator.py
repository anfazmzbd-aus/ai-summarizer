"""
V9.3-M6 deterministic summarization quality evaluator.
"""

from __future__ import annotations

import re

from .models import (
    QualityEvaluation,
    QualityMetric,
    QualityMetricName,
)


class SummarizationQualityEvaluator:
    """
    Evaluate summary quality using deterministic text metrics.

    No provider, model, network access, or API key is required.
    """

    evaluator_version = "v9.3-m6"

    def __init__(
        self,
        *,
        threshold: float = 0.60,
    ) -> None:
        if not isinstance(threshold, (int, float)):
            raise TypeError("threshold must be numeric")

        if not 0.0 <= float(threshold) <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")

        self.threshold = float(threshold)

    def evaluate(
        self,
        source: str,
        summary: str,
    ) -> QualityEvaluation:
        """
        Evaluate a summary against its source document.

        Both arguments must be strings.
        """

        if not isinstance(source, str):
            raise TypeError("source must be a string")

        if not isinstance(summary, str):
            raise TypeError("summary must be a string")

        metrics = (
            self._evaluate_non_empty(summary),
            self._evaluate_compression(
                source,
                summary,
            ),
            self._evaluate_coverage(
                source,
                summary,
            ),
            self._evaluate_repetition(summary),
        )

        score = self._aggregate(metrics)

        return QualityEvaluation(
            score=score,
            passed=score >= self.threshold,
            metrics=metrics,
            source_length=len(source),
            summary_length=len(summary),
            evaluator_version=self.evaluator_version,
            threshold=self.threshold,
            metadata={
                "metric_count": len(metrics),
                "deterministic": True,
            },
        )

    @staticmethod
    def _evaluate_non_empty(
        summary: str,
    ) -> QualityMetric:
        score = 1.0 if summary.strip() else 0.0

        return QualityMetric(
            name=QualityMetricName.NON_EMPTY,
            score=score,
            rationale=(
                "summary contains non-whitespace content"
                if score
                else "summary is empty or whitespace only"
            ),
            metadata={
                "summary_characters": len(summary),
            },
        )

    @staticmethod
    def _evaluate_compression(
        source: str,
        summary: str,
    ) -> QualityMetric:
        source_length = len(source)
        summary_length = len(summary)

        if not source_length:
            score = 1.0 if not summary_length else 0.0
        elif not summary_length:
            score = 0.0
        else:
            ratio = summary_length / source_length

            # A summary at or below 40% of the source receives full
            # compression credit. Values above the source length receive
            # zero compression credit.
            if ratio <= 0.40:
                score = 1.0
            elif ratio >= 1.0:
                score = 0.0
            else:
                score = 1.0 - (ratio - 0.40) / 0.60

        return QualityMetric(
            name=QualityMetricName.COMPRESSION,
            score=round(score, 6),
            rationale=("summary length is evaluated relative to " "source length"),
            metadata={
                "source_length": source_length,
                "summary_length": summary_length,
            },
        )

    @staticmethod
    def _evaluate_coverage(
        source: str,
        summary: str,
    ) -> QualityMetric:
        source_tokens = set(SummarizationQualityEvaluator._tokens(source))

        summary_tokens = set(SummarizationQualityEvaluator._tokens(summary))

        if not summary_tokens:
            score = 0.0
            matched = 0
        elif not source_tokens:
            score = 0.0
            matched = 0
        else:
            matched = len(source_tokens & summary_tokens)

            score = matched / len(summary_tokens)

        return QualityMetric(
            name=QualityMetricName.COVERAGE,
            score=round(
                min(1.0, score),
                6,
            ),
            rationale=(
                "measures the proportion of summary " "terms also present in the source"
            ),
            metadata={
                "source_unique_terms": len(source_tokens),
                "summary_unique_terms": len(summary_tokens),
                "matched_terms": matched,
            },
        )

    @staticmethod
    def _evaluate_repetition(
        summary: str,
    ) -> QualityMetric:
        tokens = SummarizationQualityEvaluator._tokens(summary)

        if not tokens:
            score = 0.0
            repeated = 0
        else:
            counts: dict[str, int] = {}

            for token in tokens:
                counts[token] = counts.get(token, 0) + 1

            repeated = sum(count - 1 for count in counts.values() if count > 1)

            repetition_ratio = repeated / len(tokens)

            score = max(
                0.0,
                1.0 - repetition_ratio,
            )

        return QualityMetric(
            name=QualityMetricName.REPETITION,
            score=round(score, 6),
            rationale=("penalizes repeated lexical terms"),
            metadata={
                "token_count": len(tokens),
                "repeated_tokens": repeated,
            },
        )

    @staticmethod
    def _aggregate(
        metrics: tuple[QualityMetric, ...],
    ) -> float:
        if not metrics:
            return 0.0

        score = sum(metric.score for metric in metrics) / len(metrics)

        return round(
            min(1.0, max(0.0, score)),
            6,
        )

    @staticmethod
    def _tokens(text: str) -> tuple[str, ...]:
        return tuple(
            token.lower()
            for token in re.findall(
                r"\b[\w']+\b",
                text,
            )
        )


__all__ = [
    "SummarizationQualityEvaluator",
]
