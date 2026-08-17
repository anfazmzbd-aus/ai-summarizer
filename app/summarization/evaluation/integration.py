"""
V9.3-M10 typed evaluation integration.

Provides a provider-independent adapter from existing V9.3 immutable
execution-layer models into the M10 evaluation boundary.

This module does not execute, mutate, or replace any M1-M9 component.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.summarization.planning.adaptive_models import (
    AdaptiveStrategyDecision,
)
from app.summarization.planning.models import SummarizationPlan
from app.summarization.planning.optimization_models import (
    StrategyOptimizationDecision,
)
from app.summarization.quality.models import QualityEvaluation
from app.summarization.quality_adaptive.models import (
    AdaptiveExecutionDecision,
)
from app.summarization.resilience.models import FallbackDecision
from app.summarization.streaming.models import StreamResult

from .evaluator import SummarizationEvaluationEvaluator
from .models import EvaluationResult


class V93EvaluationRecordBuilder:
    """
    Build deterministic M10 evaluation records from existing V9.3 models.

    The builder is intentionally an adapter rather than a replacement for
    any existing planning, quality, resilience, or streaming component.
    """

    builder_version = "v9.3-m10"

    def build_planning_record(
        self,
        plan: SummarizationPlan,
        adaptive: AdaptiveStrategyDecision | None = None,
    ) -> dict[str, Any]:
        """Convert a V9.3 summarization plan into an M10 planning record."""

        self._require_type(plan, SummarizationPlan, "plan")

        record: dict[str, Any] = {
            "strategy": plan.strategy.value,
            "plan": plan,
            "planner_version": plan.metadata.get("planner_version"),
            "chunk_count": plan.chunk_count,
            "token_count": plan.token_count,
            "source_character_count": plan.source_character_count,
            "source_digest": plan.source_digest,
            "intent": plan.intent.value,
        }

        if plan.document_profile is not None:
            record["document_profile"] = plan.document_profile

        if adaptive is not None:
            self._require_type(
                adaptive,
                AdaptiveStrategyDecision,
                "adaptive",
            )
            record["adaptive_strategy"] = adaptive
            record["selected_strategy"] = adaptive.selected_strategy.value
            record["promoted"] = adaptive.promoted

        return record

    def build_constraints_record(
        self,
        optimization: StrategyOptimizationDecision,
    ) -> dict[str, Any]:
        """
        Convert an M5 optimization decision into an M10 constraints record.
        """

        self._require_type(
            optimization,
            StrategyOptimizationDecision,
            "optimization",
        )

        estimates = optimization.estimates

        return {
            "strategy": optimization.selected_strategy.value,
            "baseline_strategy": optimization.baseline_strategy.value,
            "constrained": optimization.constrained,
            "reason": optimization.reason,
            "estimates": estimates,
            "token_budget": self._extract_budget(
                optimization.metadata,
                "token_budget",
            ),
            "latency_budget": self._extract_budget(
                optimization.metadata,
                "latency_budget",
            ),
            "cost_budget": self._extract_budget(
                optimization.metadata,
                "cost_budget",
            ),
            "optimization": optimization,
        }

    def build_quality_record(
        self,
        quality: QualityEvaluation,
    ) -> dict[str, Any]:
        """Convert an M6 quality evaluation into an M10 quality record."""

        self._require_type(
            quality,
            QualityEvaluation,
            "quality",
        )

        return {
            "score": quality.score,
            "passed": quality.passed,
            "threshold": quality.threshold,
            "metrics": quality.metrics,
            "source_length": quality.source_length,
            "summary_length": quality.summary_length,
            "evaluator_version": quality.evaluator_version,
            "quality": quality,
        }

    def build_resilience_record(
        self,
        decision: AdaptiveExecutionDecision | FallbackDecision,
    ) -> dict[str, Any]:
        """
        Convert M7/M8 execution decisions into an M10 resilience record.
        """

        if isinstance(decision, AdaptiveExecutionDecision):
            return {
                "action": decision.action.value,
                "current_strategy": decision.current_strategy.value,
                "next_strategy": (
                    decision.next_strategy.value
                    if decision.next_strategy is not None
                    else None
                ),
                "attempt": decision.attempt,
                "max_attempts": decision.max_attempts,
                "reason": decision.reason,
                "adaptive_execution": decision,
            }

        if isinstance(decision, FallbackDecision):
            return {
                "action": decision.action.value,
                "failed_strategy": decision.failed_strategy.value,
                "fallback_strategy": (
                    decision.fallback_strategy.value
                    if decision.fallback_strategy is not None
                    else None
                ),
                "attempted_strategies": tuple(
                    strategy.value for strategy in decision.attempted_strategies
                ),
                "max_attempts": decision.max_attempts,
                "reason": decision.reason,
                "fallback_decision": decision,
            }

        raise TypeError(
            "decision must be an AdaptiveExecutionDecision " "or FallbackDecision"
        )

    def build_streaming_record(
        self,
        result: StreamResult,
    ) -> dict[str, Any]:
        """Convert an existing streaming result into an M10 record."""

        self._require_type(
            result,
            StreamResult,
            "result",
        )

        return {
            "streamer_version": result.metadata.get("streamer_version"),
            "intelligent": bool(
                result.metadata.get("intelligent")
                or result.metadata.get("intelligence")
            ),
            "chunk_count": result.chunk_count,
            "content_length": len(result.content),
            "stream_result": result,
        }

    def evaluate(
        self,
        *,
        plan: SummarizationPlan,
        adaptive: AdaptiveStrategyDecision | None = None,
        optimization: StrategyOptimizationDecision | None = None,
        quality: QualityEvaluation | None = None,
        resilience: AdaptiveExecutionDecision | FallbackDecision | None = None,
        streaming: StreamResult | None = None,
    ) -> EvaluationResult:
        """
        Build all available M10 records and evaluate the execution state.

        The evaluator still applies its existing deterministic dimension
        semantics. Missing optional layers remain explicit failures rather
        than being silently treated as successful.
        """

        planning = self.build_planning_record(
            plan,
            adaptive,
        )

        constraints = (
            self.build_constraints_record(optimization)
            if optimization is not None
            else None
        )

        quality_record = (
            self.build_quality_record(quality) if quality is not None else None
        )

        resilience_record = (
            self.build_resilience_record(resilience) if resilience is not None else None
        )

        streaming_record = (
            self.build_streaming_record(streaming) if streaming is not None else None
        )

        evaluator = SummarizationEvaluationEvaluator()

        return evaluator.evaluate(
            planning=planning,
            constraints=constraints,
            quality=quality_record,
            resilience=resilience_record,
            streaming=streaming_record,
        )

    @staticmethod
    def _require_type(
        value: Any,
        expected_type: type,
        name: str,
    ) -> None:
        if not isinstance(value, expected_type):
            raise TypeError(f"{name} must be a {expected_type.__name__}")

    @staticmethod
    def _extract_budget(
        metadata: Mapping[str, Any],
        key: str,
    ) -> Any:
        return metadata.get(key)


__all__ = [
    "V93EvaluationRecordBuilder",
]
