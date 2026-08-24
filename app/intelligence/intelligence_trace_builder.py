"""
V10 M8 intelligence trace builder.

Validates provenance and lifecycle consistency across decision,
adaptation, and integration explanation layers, then composes one
immutable IntelligenceTrace.

M8.2 performs composition and validation only. It does not derive
observability status, generate diagnostics, or modify intelligence
behavior.
"""

from __future__ import annotations

from .adaptation_explanation import AdaptationExplanation
from .decision_explanation import DecisionExplanation
from .integration_explanation import IntegrationExplanation
from .intelligence_trace import IntelligenceTrace


class IntelligenceTraceBuilder:
    """Build a provenance-safe intelligence lifecycle trace."""

    def build(
        self,
        decision_explanation: DecisionExplanation,
        adaptation_explanation: AdaptationExplanation,
        integration_explanation: IntegrationExplanation,
    ) -> IntelligenceTrace:
        """Validate and compose the complete explanation chain."""

        self._validate_types(
            decision_explanation=decision_explanation,
            adaptation_explanation=adaptation_explanation,
            integration_explanation=integration_explanation,
        )

        self._validate_provenance(
            decision_explanation=decision_explanation,
            adaptation_explanation=adaptation_explanation,
            integration_explanation=integration_explanation,
        )

        self._validate_lifecycle_state(
            decision_explanation=decision_explanation,
            adaptation_explanation=adaptation_explanation,
        )

        return IntelligenceTrace(
            context_id=decision_explanation.context_id,
            correlation_id=decision_explanation.correlation_id,
            action=decision_explanation.action,
            decision_explanation=decision_explanation,
            adaptation_explanation=adaptation_explanation,
            integration_explanation=integration_explanation,
            historical_influence_applied=(
                adaptation_explanation.historical_influence_applied
            ),
            adaptation_applied=(adaptation_explanation.adaptation_applied),
            execution_authorized=(integration_explanation.execution_authorized),
            review_required=(integration_explanation.review_required),
        )

    @staticmethod
    def _validate_types(
        *,
        decision_explanation: DecisionExplanation,
        adaptation_explanation: AdaptationExplanation,
        integration_explanation: IntegrationExplanation,
    ) -> None:
        if not isinstance(
            decision_explanation,
            DecisionExplanation,
        ):
            raise TypeError("decision_explanation must be a DecisionExplanation")

        if not isinstance(
            adaptation_explanation,
            AdaptationExplanation,
        ):
            raise TypeError(
                "adaptation_explanation must be an " "AdaptationExplanation"
            )

        if not isinstance(
            integration_explanation,
            IntegrationExplanation,
        ):
            raise TypeError(
                "integration_explanation must be an " "IntegrationExplanation"
            )

    @staticmethod
    def _validate_provenance(
        *,
        decision_explanation: DecisionExplanation,
        adaptation_explanation: AdaptationExplanation,
        integration_explanation: IntegrationExplanation,
    ) -> None:
        context_id = decision_explanation.context_id

        if adaptation_explanation.context_id != context_id:
            raise ValueError(
                "adaptation_explanation context_id must match " "decision_explanation"
            )

        if integration_explanation.context_id != context_id:
            raise ValueError(
                "integration_explanation context_id must match " "decision_explanation"
            )

        correlation_id = decision_explanation.correlation_id

        if adaptation_explanation.correlation_id != correlation_id:
            raise ValueError(
                "adaptation_explanation correlation_id must match "
                "decision_explanation"
            )

        if integration_explanation.correlation_id != correlation_id:
            raise ValueError(
                "integration_explanation correlation_id must match "
                "decision_explanation"
            )

        action = decision_explanation.action

        if adaptation_explanation.action is not action:
            raise ValueError(
                "adaptation_explanation action must match " "decision_explanation"
            )

        if integration_explanation.action is not action:
            raise ValueError(
                "integration_explanation action must match " "decision_explanation"
            )

    @staticmethod
    def _validate_lifecycle_state(
        *,
        decision_explanation: DecisionExplanation,
        adaptation_explanation: AdaptationExplanation,
    ) -> None:
        if (
            decision_explanation.historical_influence_applied
            is not adaptation_explanation.historical_influence_applied
        ):
            raise ValueError(
                "historical influence must match across "
                "decision and adaptation explanations"
            )


__all__ = ["IntelligenceTraceBuilder"]
