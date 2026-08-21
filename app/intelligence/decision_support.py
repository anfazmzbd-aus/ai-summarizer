"""
V10 bounded decision support contracts.

Transforms historical evidence assessment into a deterministic,
explainable support assessment for an existing TaskDecision.

M5.3 does not apply policy, modify the decision, select alternatives,
or interact with runtime/providers.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from .evidence_evaluation import (
    EvidenceAssessment,
    EvidenceAssessmentStatus,
)
from .experience_evidence import EvidenceStrength
from .task_decision import TaskAction, TaskDecision


class DecisionSupportStatus(str, Enum):
    """Historical support state for an existing task decision."""

    SUPPORTED = "supported"
    CAUTION = "caution"
    UNSUPPORTED = "unsupported"
    NEUTRAL = "neutral"


@dataclass(frozen=True, slots=True)
class DecisionSupportAssessment:
    """
    Immutable historical support assessment for one TaskDecision.

    The assessment describes whether historical evidence supports,
    cautions against, or does not materially inform the existing action.

    It does not prescribe a replacement action.
    """

    context_id: UUID
    correlation_id: UUID

    action: TaskAction
    support_status: DecisionSupportStatus

    evidence_status: EvidenceAssessmentStatus
    evidence_strength: EvidenceStrength

    sample_count: int
    known_count: int
    unknown_count: int

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

        counts = {
            "sample_count": self.sample_count,
            "known_count": self.known_count,
            "unknown_count": self.unknown_count,
        }

        for name, value in counts.items():
            if not isinstance(value, int) or isinstance(
                value,
                bool,
            ):
                raise TypeError(f"{name} must be an integer")

            if value < 0:
                raise ValueError(f"{name} must be greater than or equal to 0")

        if self.known_count + self.unknown_count != self.sample_count:
            raise ValueError("known_count and unknown_count must sum to sample_count")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        expected_support = self._expected_support_status(self.evidence_status)

        if self.support_status is not expected_support:
            raise ValueError("support_status must match evidence_status")

    @staticmethod
    def _expected_support_status(
        status: EvidenceAssessmentStatus,
    ) -> DecisionSupportStatus:
        if status is EvidenceAssessmentStatus.SUPPORTIVE:
            return DecisionSupportStatus.SUPPORTED

        if status is EvidenceAssessmentStatus.CAUTIONARY:
            return DecisionSupportStatus.CAUTION

        if status is EvidenceAssessmentStatus.ADVERSE:
            return DecisionSupportStatus.UNSUPPORTED

        return DecisionSupportStatus.NEUTRAL

    @classmethod
    def create(
        cls,
        *,
        context_id: UUID,
        correlation_id: UUID,
        action: TaskAction,
        evidence_status: EvidenceAssessmentStatus,
        evidence_strength: EvidenceStrength,
        sample_count: int,
        known_count: int,
        unknown_count: int,
        reasons: tuple[str, ...],
    ) -> "DecisionSupportAssessment":
        """Create support with deterministically derived support status."""

        if not isinstance(
            evidence_status,
            EvidenceAssessmentStatus,
        ):
            raise TypeError("evidence_status must be an EvidenceAssessmentStatus")

        return cls(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
            support_status=cls._expected_support_status(evidence_status),
            evidence_status=evidence_status,
            evidence_strength=evidence_strength,
            sample_count=sample_count,
            known_count=known_count,
            unknown_count=unknown_count,
            reasons=reasons,
        )


class DecisionSupportBuilder:
    """
    Build historical decision support for an existing TaskDecision.

    The builder interprets an already-evaluated evidence assessment only.
    It does not apply decision policy.
    """

    def build(
        self,
        decision: TaskDecision,
        assessment: EvidenceAssessment,
    ) -> DecisionSupportAssessment:
        """Build deterministic support for the existing decision."""

        if not isinstance(decision, TaskDecision):
            raise TypeError("decision must be a TaskDecision")

        if not isinstance(
            assessment,
            EvidenceAssessment,
        ):
            raise TypeError("assessment must be an EvidenceAssessment")

        if decision.action is not assessment.action:
            raise ValueError("decision and assessment action must match")

        reasons = self._build_reasons(
            decision=decision,
            assessment=assessment,
        )

        return DecisionSupportAssessment.create(
            context_id=decision.context_id,
            correlation_id=decision.correlation_id,
            action=decision.action,
            evidence_status=assessment.status,
            evidence_strength=assessment.evidence_strength,
            sample_count=assessment.sample_count,
            known_count=assessment.known_count,
            unknown_count=assessment.unknown_count,
            reasons=reasons,
        )

    @staticmethod
    def _build_reasons(
        *,
        decision: TaskDecision,
        assessment: EvidenceAssessment,
    ) -> tuple[str, ...]:
        reasons: list[str] = list(assessment.reasons)

        if assessment.status is EvidenceAssessmentStatus.SUPPORTIVE:
            reasons.append("historical evidence supports the current action")

        elif assessment.status is EvidenceAssessmentStatus.CAUTIONARY:
            reasons.append(
                "historical evidence warrants caution for the current action"
            )

        elif assessment.status is EvidenceAssessmentStatus.ADVERSE:
            reasons.append("historical evidence does not support the current action")

        elif assessment.status is EvidenceAssessmentStatus.NO_EVIDENCE:
            reasons.append("historical evidence does not inform the current action")

        elif assessment.status is EvidenceAssessmentStatus.INSUFFICIENT:
            reasons.append(
                "historical evidence is insufficient to support "
                "or oppose the current action"
            )

        else:
            reasons.append(
                "historical evidence is mixed and does not establish "
                "directional support"
            )

        return tuple(reasons)


__all__ = [
    "DecisionSupportAssessment",
    "DecisionSupportBuilder",
    "DecisionSupportStatus",
]
