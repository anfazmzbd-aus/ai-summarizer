"""
V10 adaptive policy composition boundary.

Composes the completed M6 adaptation contracts into one immutable outcome
suitable for later orchestration integration.

M6.6 does not execute adaptation, alter runtime state, select providers,
change strategies, retry work, or modify TaskDecision.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .adaptation_decision import (
    AdaptationDecision,
    AdaptationDisposition,
)
from .adaptation_eligibility import (
    AdaptationEligibility,
    AdaptationEligibilityStatus,
)
from .adaptation_explanation import (
    AdaptationExplanation,
)
from .decision_support_policy import (
    DecisionSupportDisposition,
)
from .experience_informed_decision import (
    ExperienceInformedDecision,
)
from .task_decision import TaskAction


@dataclass(frozen=True, slots=True)
class AdaptivePolicyOutcome:
    """
    Immutable result of the complete bounded adaptation policy chain.

    This outcome is the M6 handoff contract for later orchestration
    integration. It contains intent only and no runtime instruction.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    informed_decision: ExperienceInformedDecision
    eligibility: AdaptationEligibility
    adaptation_decision: AdaptationDecision
    explanation: AdaptationExplanation

    policy_disposition: DecisionSupportDisposition
    eligibility_status: AdaptationEligibilityStatus
    adaptation_disposition: AdaptationDisposition

    historical_influence_applied: bool
    adaptation_applied: bool

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(
            self.informed_decision,
            ExperienceInformedDecision,
        ):
            raise TypeError(
                "informed_decision must be an " "ExperienceInformedDecision"
            )

        if not isinstance(
            self.eligibility,
            AdaptationEligibility,
        ):
            raise TypeError("eligibility must be an AdaptationEligibility")

        if not isinstance(
            self.adaptation_decision,
            AdaptationDecision,
        ):
            raise TypeError("adaptation_decision must be an AdaptationDecision")

        if not isinstance(
            self.explanation,
            AdaptationExplanation,
        ):
            raise TypeError("explanation must be an AdaptationExplanation")

        if not isinstance(
            self.policy_disposition,
            DecisionSupportDisposition,
        ):
            raise TypeError(
                "policy_disposition must be a " "DecisionSupportDisposition"
            )

        if not isinstance(
            self.eligibility_status,
            AdaptationEligibilityStatus,
        ):
            raise TypeError(
                "eligibility_status must be an " "AdaptationEligibilityStatus"
            )

        if not isinstance(
            self.adaptation_disposition,
            AdaptationDisposition,
        ):
            raise TypeError(
                "adaptation_disposition must be an " "AdaptationDisposition"
            )

        if not isinstance(
            self.historical_influence_applied,
            bool,
        ):
            raise TypeError("historical_influence_applied must be a bool")

        if not isinstance(
            self.adaptation_applied,
            bool,
        ):
            raise TypeError("adaptation_applied must be a bool")

        self._validate_consistency()

    def _validate_consistency(self) -> None:
        decision = self.informed_decision.decision

        if self.context_id != decision.context_id:
            raise ValueError("context_id must match informed decision")

        if self.correlation_id != decision.correlation_id:
            raise ValueError("correlation_id must match informed decision")

        if self.action is not decision.action:
            raise ValueError("action must match informed decision")

        if self.eligibility.context_id != self.context_id:
            raise ValueError("eligibility context_id must match outcome")

        if self.eligibility.correlation_id != self.correlation_id:
            raise ValueError("eligibility correlation_id must match outcome")

        if self.eligibility.action is not self.action:
            raise ValueError("eligibility action must match outcome")

        if self.adaptation_decision.context_id != self.context_id:
            raise ValueError("adaptation_decision context_id must match outcome")

        if self.adaptation_decision.correlation_id != self.correlation_id:
            raise ValueError("adaptation_decision correlation_id must match outcome")

        if self.adaptation_decision.action is not self.action:
            raise ValueError("adaptation_decision action must match outcome")

        if self.explanation.context_id != self.context_id:
            raise ValueError("explanation context_id must match outcome")

        if self.explanation.correlation_id != self.correlation_id:
            raise ValueError("explanation correlation_id must match outcome")

        if self.explanation.action is not self.action:
            raise ValueError("explanation action must match outcome")

        if (
            self.policy_disposition
            is not self.informed_decision.policy_result.disposition
        ):
            raise ValueError("policy_disposition must match informed decision")

        if self.eligibility_status is not self.eligibility.status:
            raise ValueError("eligibility_status must match eligibility")

        if self.adaptation_disposition is not self.adaptation_decision.disposition:
            raise ValueError("adaptation_disposition must match " "adaptation_decision")

        if (
            self.historical_influence_applied
            is not self.informed_decision.historical_influence_applied
        ):
            raise ValueError(
                "historical_influence_applied must match " "informed_decision"
            )

        if self.adaptation_applied is not self.adaptation_decision.adaptation_applied:
            raise ValueError("adaptation_applied must match adaptation_decision")


class AdaptivePolicyCompositionBoundary:
    """Compose the complete bounded M6 adaptation chain."""

    def compose(
        self,
        informed_decision: ExperienceInformedDecision,
        eligibility: AdaptationEligibility,
        adaptation_decision: AdaptationDecision,
        explanation: AdaptationExplanation,
    ) -> AdaptivePolicyOutcome:
        """Create one validated M6 adaptive policy outcome."""

        self._validate_types(
            informed_decision=informed_decision,
            eligibility=eligibility,
            adaptation_decision=adaptation_decision,
            explanation=explanation,
        )

        return AdaptivePolicyOutcome(
            context_id=informed_decision.decision.context_id,
            correlation_id=(informed_decision.decision.correlation_id),
            action=informed_decision.decision.action,
            informed_decision=informed_decision,
            eligibility=eligibility,
            adaptation_decision=adaptation_decision,
            explanation=explanation,
            policy_disposition=(informed_decision.policy_result.disposition),
            eligibility_status=eligibility.status,
            adaptation_disposition=(adaptation_decision.disposition),
            historical_influence_applied=(
                informed_decision.historical_influence_applied
            ),
            adaptation_applied=(adaptation_decision.adaptation_applied),
        )

    @staticmethod
    def _validate_types(
        *,
        informed_decision: ExperienceInformedDecision,
        eligibility: AdaptationEligibility,
        adaptation_decision: AdaptationDecision,
        explanation: AdaptationExplanation,
    ) -> None:
        if not isinstance(
            informed_decision,
            ExperienceInformedDecision,
        ):
            raise TypeError(
                "informed_decision must be an " "ExperienceInformedDecision"
            )

        if not isinstance(
            eligibility,
            AdaptationEligibility,
        ):
            raise TypeError("eligibility must be an AdaptationEligibility")

        if not isinstance(
            adaptation_decision,
            AdaptationDecision,
        ):
            raise TypeError("adaptation_decision must be an AdaptationDecision")

        if not isinstance(
            explanation,
            AdaptationExplanation,
        ):
            raise TypeError("explanation must be an AdaptationExplanation")


__all__ = [
    "AdaptivePolicyCompositionBoundary",
    "AdaptivePolicyOutcome",
]
