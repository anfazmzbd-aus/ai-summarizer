"""
V10 M8 intelligence observability summary evaluator.

Derives a compact operational IntelligenceObservabilitySummary from a
validated IntelligenceTrace.

M8.4 performs deterministic read-only evaluation only. It does not alter
intelligence decisions, adaptation, orchestration, or runtime behavior.
"""

from __future__ import annotations

from .execution_integration import ExecutionIntegrationMode
from .intelligence_trace import IntelligenceTrace
from .observability_summary import (
    IntelligenceObservabilityStatus,
    IntelligenceObservabilitySummary,
)


class IntelligenceObservabilityEvaluator:
    """Evaluate one intelligence trace into a compact observability summary."""

    def evaluate(
        self,
        trace: IntelligenceTrace,
    ) -> IntelligenceObservabilitySummary:
        """Derive an immutable observability summary."""

        if not isinstance(trace, IntelligenceTrace):
            raise TypeError("trace must be an IntelligenceTrace")

        self._validate_trace_consistency(trace)

        integration = trace.integration_explanation
        adaptation = trace.adaptation_explanation

        status = self._derive_status(integration.integration_mode)

        reason_count = self._derive_reason_count(trace)

        return IntelligenceObservabilitySummary(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            status=status,
            adaptation_disposition=(adaptation.adaptation_disposition),
            orchestration_disposition=(integration.orchestration_disposition),
            integration_mode=integration.integration_mode,
            historical_influence_applied=(trace.historical_influence_applied),
            adaptation_applied=trace.adaptation_applied,
            execution_authorized=trace.execution_authorized,
            review_required=trace.review_required,
            reason_count=reason_count,
        )

    @staticmethod
    def _validate_trace_consistency(
        trace: IntelligenceTrace,
    ) -> None:
        decision = trace.decision_explanation
        adaptation = trace.adaptation_explanation
        integration = trace.integration_explanation

        if trace.context_id != decision.context_id:
            raise ValueError("trace context_id must match decision_explanation")

        if trace.correlation_id != decision.correlation_id:
            raise ValueError("trace correlation_id must match decision_explanation")

        if trace.action is not decision.action:
            raise ValueError("trace action must match decision_explanation")

        if adaptation.context_id != trace.context_id:
            raise ValueError("adaptation_explanation context_id must match trace")

        if adaptation.correlation_id != trace.correlation_id:
            raise ValueError("adaptation_explanation correlation_id must match trace")

        if adaptation.action is not trace.action:
            raise ValueError("adaptation_explanation action must match trace")

        if integration.context_id != trace.context_id:
            raise ValueError("integration_explanation context_id must match trace")

        if integration.correlation_id != trace.correlation_id:
            raise ValueError("integration_explanation correlation_id must match trace")

        if integration.action is not trace.action:
            raise ValueError("integration_explanation action must match trace")

        if (
            trace.historical_influence_applied
            is not adaptation.historical_influence_applied
        ):
            raise ValueError(
                "trace historical influence must match " "adaptation_explanation"
            )

        if trace.adaptation_applied is not adaptation.adaptation_applied:
            raise ValueError(
                "trace adaptation state must match " "adaptation_explanation"
            )

        if trace.execution_authorized is not integration.execution_authorized:
            raise ValueError(
                "trace execution authority must match " "integration_explanation"
            )

        if trace.review_required is not integration.review_required:
            raise ValueError(
                "trace review requirement must match " "integration_explanation"
            )

        if adaptation.adaptation_disposition is not integration.adaptation_disposition:
            raise ValueError(
                "adaptation disposition must match across "
                "adaptation and integration explanations"
            )

    @staticmethod
    def _derive_status(
        integration_mode: ExecutionIntegrationMode,
    ) -> IntelligenceObservabilityStatus:
        if integration_mode is ExecutionIntegrationMode.PRESERVE:
            return IntelligenceObservabilityStatus.NORMAL

        if integration_mode is ExecutionIntegrationMode.ADVISORY:
            return IntelligenceObservabilityStatus.ADVISORY

        if integration_mode is ExecutionIntegrationMode.CONSTRAINED:
            return IntelligenceObservabilityStatus.CONSTRAINED

        if integration_mode is ExecutionIntegrationMode.REVIEW:
            return IntelligenceObservabilityStatus.REVIEW_REQUIRED

        raise ValueError("unsupported execution integration mode")

    @staticmethod
    def _derive_reason_count(
        trace: IntelligenceTrace,
    ) -> int:
        decision = trace.decision_explanation
        adaptation = trace.adaptation_explanation
        integration = trace.integration_explanation

        return sum(
            len(reasons)
            for reasons in (
                decision.evidence_reasons,
                decision.support_reasons,
                decision.policy_reasons,
                decision.decision_reasons,
                adaptation.informed_decision_reasons,
                adaptation.eligibility_reasons,
                adaptation.adaptation_reasons,
                integration.orchestration_reasons,
                integration.validation_reasons,
                integration.integration_reasons,
            )
        )


__all__ = ["IntelligenceObservabilityEvaluator"]
