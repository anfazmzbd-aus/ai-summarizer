"""
V10 adaptation explainability and provenance boundary.

Produces an immutable audit representation of bounded adaptation decisions.

M6.5 adds no adaptation semantics and performs no runtime actions.
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
from .decision_support_policy import (
    DecisionSupportDisposition,
)
from .experience_informed_decision import (
    ExperienceInformedDecision,
)
from .task_decision import TaskAction


@dataclass(frozen=True, slots=True)
class AdaptationExplanation:
    """
    Immutable audit trace for one bounded adaptation decision.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    policy_disposition: DecisionSupportDisposition
    eligibility_status: AdaptationEligibilityStatus
    adaptation_disposition: AdaptationDisposition

    historical_influence_applied: bool
    adaptation_applied: bool

    informed_decision_reasons: tuple[str, ...]
    eligibility_reasons: tuple[str, ...]
    adaptation_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

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

        for field_name, reasons in (
            (
                "informed_decision_reasons",
                self.informed_decision_reasons,
            ),
            (
                "eligibility_reasons",
                self.eligibility_reasons,
            ),
            (
                "adaptation_reasons",
                self.adaptation_reasons,
            ),
        ):
            if not isinstance(reasons, tuple):
                raise TypeError(f"{field_name} must be a tuple")

            for reason in reasons:
                if not isinstance(reason, str):
                    raise TypeError(f"{field_name} must contain strings")


class AdaptationExplanationBuilder:
    """Build a deterministic audit trace for bounded adaptation."""

    def build(
        self,
        informed_decision: ExperienceInformedDecision,
        eligibility: AdaptationEligibility,
        adaptation_decision: AdaptationDecision,
    ) -> AdaptationExplanation:
        """Build one validated adaptation explanation."""

        self._validate_types(
            informed_decision=informed_decision,
            eligibility=eligibility,
            adaptation_decision=adaptation_decision,
        )

        self._validate_chain(
            informed_decision=informed_decision,
            eligibility=eligibility,
            adaptation_decision=adaptation_decision,
        )

        decision = informed_decision.decision

        return AdaptationExplanation(
            context_id=decision.context_id,
            correlation_id=decision.correlation_id,
            action=decision.action,
            policy_disposition=(informed_decision.policy_result.disposition),
            eligibility_status=eligibility.status,
            adaptation_disposition=(adaptation_decision.disposition),
            historical_influence_applied=(
                informed_decision.historical_influence_applied
            ),
            adaptation_applied=(adaptation_decision.adaptation_applied),
            informed_decision_reasons=(informed_decision.reasons),
            eligibility_reasons=eligibility.reasons,
            adaptation_reasons=adaptation_decision.reasons,
        )

    @staticmethod
    def _validate_types(
        *,
        informed_decision: ExperienceInformedDecision,
        eligibility: AdaptationEligibility,
        adaptation_decision: AdaptationDecision,
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
            raise TypeError("adaptation_decision must be an " "AdaptationDecision")

    @staticmethod
    def _validate_chain(
        *,
        informed_decision: ExperienceInformedDecision,
        eligibility: AdaptationEligibility,
        adaptation_decision: AdaptationDecision,
    ) -> None:
        decision = informed_decision.decision
        policy_result = informed_decision.policy_result

        if decision.context_id != eligibility.context_id:
            raise ValueError("decision and eligibility context_id must match")

        if decision.correlation_id != eligibility.correlation_id:
            raise ValueError("decision and eligibility correlation_id must match")

        if decision.action is not eligibility.action:
            raise ValueError("decision and eligibility action must match")

        if policy_result.disposition is not eligibility.policy_disposition:
            raise ValueError("policy disposition must match eligibility")

        if (
            informed_decision.historical_influence_applied
            is not eligibility.historical_influence_applied
        ):
            raise ValueError("historical influence must match eligibility")

        if adaptation_decision.context_id != eligibility.context_id:
            raise ValueError("adaptation_decision context_id must match " "eligibility")

        if adaptation_decision.correlation_id != eligibility.correlation_id:
            raise ValueError(
                "adaptation_decision correlation_id must match " "eligibility"
            )

        if adaptation_decision.action is not eligibility.action:
            raise ValueError("adaptation_decision action must match eligibility")

        if adaptation_decision.eligibility_status is not eligibility.status:
            raise ValueError(
                "adaptation_decision eligibility_status must " "match eligibility"
            )


__all__ = [
    "AdaptationExplanation",
    "AdaptationExplanationBuilder",
]
