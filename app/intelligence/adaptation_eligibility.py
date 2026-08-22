"""
V10 adaptation eligibility contract.

Defines the immutable boundary describing whether an
experience-informed decision is eligible for later bounded adaptation.

M6.1 defines representation only. It does not evaluate eligibility,
select adaptations, modify decisions, or invoke runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from .decision_support_policy import DecisionSupportDisposition
from .task_decision import TaskAction


class AdaptationEligibilityStatus(str, Enum):
    """Eligibility state for later bounded adaptation."""

    INELIGIBLE = "ineligible"
    ELIGIBLE = "eligible"
    REVIEW_ONLY = "review_only"


@dataclass(frozen=True, slots=True)
class AdaptationEligibility:
    """
    Immutable adaptation eligibility result.

    This contract records eligibility only. It contains no adaptation
    instruction and cannot modify execution behavior.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction
    policy_disposition: DecisionSupportDisposition
    historical_influence_applied: bool
    status: AdaptationEligibilityStatus
    reasons: tuple[str, ...]

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
            self.historical_influence_applied,
            bool,
        ):
            raise TypeError("historical_influence_applied must be a bool")

        if not isinstance(
            self.status,
            AdaptationEligibilityStatus,
        ):
            raise TypeError("status must be an AdaptationEligibilityStatus")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

    @classmethod
    def create(
        cls,
        *,
        context_id: UUID,
        correlation_id: UUID,
        action: TaskAction,
        policy_disposition: DecisionSupportDisposition,
        historical_influence_applied: bool,
        status: AdaptationEligibilityStatus,
        reasons: tuple[str, ...],
    ) -> "AdaptationEligibility":
        """Create an immutable adaptation eligibility result."""

        return cls(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
            policy_disposition=policy_disposition,
            historical_influence_applied=(historical_influence_applied),
            status=status,
            reasons=reasons,
        )


__all__ = [
    "AdaptationEligibility",
    "AdaptationEligibilityStatus",
]
