"""
V10 bounded decision support policy.

Applies conservative policy semantics to DecisionSupportAssessment.

The policy determines whether historical evidence should be preserved as
neutral context, treated as advisory, treated with caution, or surfaced
for review.

It never replaces TaskDecision, executes runtime actions, changes providers,
selects strategies, retries work, or performs replanning.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from .decision_support import (
    DecisionSupportAssessment,
    DecisionSupportStatus,
)
from .evidence_evaluation import EvidenceAssessmentStatus
from .experience_evidence import EvidenceStrength
from .task_decision import TaskAction


class DecisionSupportDisposition(str, Enum):
    """Bounded policy disposition for historical decision support."""

    PRESERVE = "preserve"
    ADVISORY = "advisory"
    CAUTION = "caution"
    REVIEW = "review"


@dataclass(frozen=True, slots=True)
class DecisionSupportPolicyResult:
    """
    Immutable result of bounded historical-support policy evaluation.

    The result describes how historical evidence may be considered by
    later intelligence. It contains no replacement decision or runtime
    command.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    support_status: DecisionSupportStatus
    evidence_status: EvidenceAssessmentStatus
    evidence_strength: EvidenceStrength

    disposition: DecisionSupportDisposition

    historical_influence_allowed: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(
            self.support_status,
            DecisionSupportStatus,
        ):
            raise TypeError("support_status must be a DecisionSupportStatus")

        if not isinstance(
            self.evidence_status,
            EvidenceAssessmentStatus,
        ):
            raise TypeError("evidence_status must be an EvidenceAssessmentStatus")

        if not isinstance(
            self.evidence_strength,
            EvidenceStrength,
        ):
            raise TypeError("evidence_strength must be an EvidenceStrength")

        if not isinstance(
            self.disposition,
            DecisionSupportDisposition,
        ):
            raise TypeError("disposition must be a DecisionSupportDisposition")

        if not isinstance(
            self.historical_influence_allowed,
            bool,
        ):
            raise TypeError("historical_influence_allowed must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        expected_allowed = self.disposition is not DecisionSupportDisposition.PRESERVE

        if self.historical_influence_allowed is not expected_allowed:
            raise ValueError("historical_influence_allowed must match disposition")

    @classmethod
    def create(
        cls,
        *,
        context_id: UUID,
        correlation_id: UUID,
        action: TaskAction,
        support_status: DecisionSupportStatus,
        evidence_status: EvidenceAssessmentStatus,
        evidence_strength: EvidenceStrength,
        disposition: DecisionSupportDisposition,
        reasons: tuple[str, ...],
    ) -> "DecisionSupportPolicyResult":
        """Create an immutable policy result."""

        return cls(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
            support_status=support_status,
            evidence_status=evidence_status,
            evidence_strength=evidence_strength,
            disposition=disposition,
            historical_influence_allowed=(
                disposition is not DecisionSupportDisposition.PRESERVE
            ),
            reasons=reasons,
        )


class BoundedDecisionSupportPolicy:
    """
    Apply conservative policy to historical decision support.

    Historical evidence becomes influential only when it is directional
    and supported by established evidence.
    """

    def apply(
        self,
        support: DecisionSupportAssessment,
    ) -> DecisionSupportPolicyResult:
        """Apply bounded deterministic policy."""

        if not isinstance(
            support,
            DecisionSupportAssessment,
        ):
            raise TypeError("support must be a DecisionSupportAssessment")

        disposition = self._derive_disposition(support)

        reasons = self._build_reasons(
            support=support,
            disposition=disposition,
        )

        return DecisionSupportPolicyResult.create(
            context_id=support.context_id,
            correlation_id=support.correlation_id,
            action=support.action,
            support_status=support.support_status,
            evidence_status=support.evidence_status,
            evidence_strength=support.evidence_strength,
            disposition=disposition,
            reasons=reasons,
        )

    @staticmethod
    def _derive_disposition(
        support: DecisionSupportAssessment,
    ) -> DecisionSupportDisposition:
        if support.evidence_strength is not EvidenceStrength.ESTABLISHED:
            return DecisionSupportDisposition.PRESERVE

        if support.support_status is DecisionSupportStatus.SUPPORTED:
            return DecisionSupportDisposition.ADVISORY

        if support.support_status is DecisionSupportStatus.CAUTION:
            return DecisionSupportDisposition.CAUTION

        if support.support_status is DecisionSupportStatus.UNSUPPORTED:
            return DecisionSupportDisposition.REVIEW

        return DecisionSupportDisposition.PRESERVE

    @staticmethod
    def _build_reasons(
        *,
        support: DecisionSupportAssessment,
        disposition: DecisionSupportDisposition,
    ) -> tuple[str, ...]:
        reasons: list[str] = list(support.reasons)

        if support.evidence_strength is not EvidenceStrength.ESTABLISHED:
            reasons.append(
                "historical evidence is not established enough "
                "to influence decision policy"
            )
            return tuple(reasons)

        if disposition is DecisionSupportDisposition.ADVISORY:
            reasons.append(
                "established historical evidence may be used " "as advisory support"
            )

        elif disposition is DecisionSupportDisposition.CAUTION:
            reasons.append(
                "established historical evidence may be used " "as cautionary context"
            )

        elif disposition is DecisionSupportDisposition.REVIEW:
            reasons.append(
                "established adverse historical evidence " "warrants decision review"
            )

        else:
            reasons.append(
                "historical evidence does not establish "
                "a directional policy influence"
            )

        return tuple(reasons)


__all__ = [
    "BoundedDecisionSupportPolicy",
    "DecisionSupportDisposition",
    "DecisionSupportPolicyResult",
]
