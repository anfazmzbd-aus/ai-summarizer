"""
V10 adaptation decision contract.

Defines the immutable result representing a bounded adaptation disposition.

M6.3 defines representation only. It does not evaluate policy, modify
TaskDecision, invoke runtime behavior, select strategies/providers,
or execute adaptation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from .adaptation_eligibility import (
    AdaptationEligibilityStatus,
)
from .task_decision import TaskAction


class AdaptationDisposition(str, Enum):
    """Bounded adaptation disposition."""

    PRESERVE = "preserve"
    ADVISORY = "advisory"
    CONSTRAIN = "constrain"
    REVIEW = "review"


@dataclass(frozen=True, slots=True)
class AdaptationDecision:
    """
    Immutable bounded adaptation result.

    The decision describes permitted adaptation intent only.
    It contains no runtime configuration or execution instruction.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    eligibility_status: AdaptationEligibilityStatus
    disposition: AdaptationDisposition

    adaptation_applied: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(
            self.eligibility_status,
            AdaptationEligibilityStatus,
        ):
            raise TypeError(
                "eligibility_status must be an " "AdaptationEligibilityStatus"
            )

        if not isinstance(
            self.disposition,
            AdaptationDisposition,
        ):
            raise TypeError("disposition must be an AdaptationDisposition")

        if not isinstance(
            self.adaptation_applied,
            bool,
        ):
            raise TypeError("adaptation_applied must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        expected_applied = self.disposition is not AdaptationDisposition.PRESERVE

        if self.adaptation_applied is not expected_applied:
            raise ValueError("adaptation_applied must match disposition")

    @classmethod
    def create(
        cls,
        *,
        context_id: UUID,
        correlation_id: UUID,
        action: TaskAction,
        eligibility_status: AdaptationEligibilityStatus,
        disposition: AdaptationDisposition,
        reasons: tuple[str, ...],
    ) -> "AdaptationDecision":
        """Create an immutable adaptation decision."""

        return cls(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
            eligibility_status=eligibility_status,
            disposition=disposition,
            adaptation_applied=(disposition is not AdaptationDisposition.PRESERVE),
            reasons=reasons,
        )


__all__ = [
    "AdaptationDecision",
    "AdaptationDisposition",
]
