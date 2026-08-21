"""
V10 decision explainability and provenance boundary.

Produces one immutable audit representation of the complete bounded
experience-informed decision chain.

M5.6 adds no decision semantics and performs no runtime actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .decision_support import (
    DecisionSupportAssessment,
    DecisionSupportStatus,
)
from .decision_support_policy import (
    DecisionSupportDisposition,
    DecisionSupportPolicyResult,
)
from .evidence_evaluation import (
    EvidenceAssessment,
    EvidenceAssessmentStatus,
)
from .experience_evidence import (
    EvidenceStrength,
    ExperienceEvidence,
)
from .experience_informed_decision import (
    ExperienceInformedDecision,
)
from .task_decision import TaskAction


@dataclass(frozen=True, slots=True)
class DecisionExplanation:
    """
    Immutable audit trace for one experience-informed decision.

    The explanation captures provenance, historical evidence,
    interpretation, support, policy, and final bounded influence state.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    sample_count: int
    effective_count: int
    degraded_count: int
    ineffective_count: int
    unknown_count: int

    evidence_strength: EvidenceStrength
    evidence_status: EvidenceAssessmentStatus
    support_status: DecisionSupportStatus
    disposition: DecisionSupportDisposition

    historical_influence_applied: bool

    evidence_reasons: tuple[str, ...]
    support_reasons: tuple[str, ...]
    policy_reasons: tuple[str, ...]
    decision_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        counts = {
            "sample_count": self.sample_count,
            "effective_count": self.effective_count,
            "degraded_count": self.degraded_count,
            "ineffective_count": self.ineffective_count,
            "unknown_count": self.unknown_count,
        }

        for name, value in counts.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be an integer")

            if value < 0:
                raise ValueError(f"{name} must be greater than or equal to 0")

        categorized_total = (
            self.effective_count
            + self.degraded_count
            + self.ineffective_count
            + self.unknown_count
        )

        if categorized_total != self.sample_count:
            raise ValueError("effectiveness counts must sum to sample_count")

        if not isinstance(
            self.evidence_strength,
            EvidenceStrength,
        ):
            raise TypeError("evidence_strength must be an EvidenceStrength")

        if not isinstance(
            self.evidence_status,
            EvidenceAssessmentStatus,
        ):
            raise TypeError("evidence_status must be an EvidenceAssessmentStatus")

        if not isinstance(
            self.support_status,
            DecisionSupportStatus,
        ):
            raise TypeError("support_status must be a DecisionSupportStatus")

        if not isinstance(
            self.disposition,
            DecisionSupportDisposition,
        ):
            raise TypeError("disposition must be a DecisionSupportDisposition")

        if not isinstance(
            self.historical_influence_applied,
            bool,
        ):
            raise TypeError("historical_influence_applied must be a bool")

        for field_name, reasons in (
            ("evidence_reasons", self.evidence_reasons),
            ("support_reasons", self.support_reasons),
            ("policy_reasons", self.policy_reasons),
            ("decision_reasons", self.decision_reasons),
        ):
            if not isinstance(reasons, tuple):
                raise TypeError(f"{field_name} must be a tuple")

            for reason in reasons:
                if not isinstance(reason, str):
                    raise TypeError(f"{field_name} must contain strings")


class DecisionExplanationBuilder:
    """Build a deterministic explanation from the complete M5 chain."""

    def build(
        self,
        evidence: ExperienceEvidence,
        assessment: EvidenceAssessment,
        support: DecisionSupportAssessment,
        policy_result: DecisionSupportPolicyResult,
        informed_decision: ExperienceInformedDecision,
    ) -> DecisionExplanation:
        """Build one validated audit trace."""

        self._validate_types(
            evidence=evidence,
            assessment=assessment,
            support=support,
            policy_result=policy_result,
            informed_decision=informed_decision,
        )

        self._validate_chain(
            evidence=evidence,
            assessment=assessment,
            support=support,
            policy_result=policy_result,
            informed_decision=informed_decision,
        )

        decision = informed_decision.decision

        return DecisionExplanation(
            context_id=decision.context_id,
            correlation_id=decision.correlation_id,
            action=decision.action,
            sample_count=evidence.sample_count,
            effective_count=evidence.effective_count,
            degraded_count=evidence.degraded_count,
            ineffective_count=evidence.ineffective_count,
            unknown_count=evidence.unknown_count,
            evidence_strength=evidence.strength,
            evidence_status=assessment.status,
            support_status=support.support_status,
            disposition=policy_result.disposition,
            historical_influence_applied=(
                informed_decision.historical_influence_applied
            ),
            evidence_reasons=assessment.reasons,
            support_reasons=support.reasons,
            policy_reasons=policy_result.reasons,
            decision_reasons=informed_decision.reasons,
        )

    @staticmethod
    def _validate_types(
        *,
        evidence: ExperienceEvidence,
        assessment: EvidenceAssessment,
        support: DecisionSupportAssessment,
        policy_result: DecisionSupportPolicyResult,
        informed_decision: ExperienceInformedDecision,
    ) -> None:
        if not isinstance(evidence, ExperienceEvidence):
            raise TypeError("evidence must be an ExperienceEvidence")

        if not isinstance(assessment, EvidenceAssessment):
            raise TypeError("assessment must be an EvidenceAssessment")

        if not isinstance(
            support,
            DecisionSupportAssessment,
        ):
            raise TypeError("support must be a DecisionSupportAssessment")

        if not isinstance(
            policy_result,
            DecisionSupportPolicyResult,
        ):
            raise TypeError("policy_result must be a DecisionSupportPolicyResult")

        if not isinstance(
            informed_decision,
            ExperienceInformedDecision,
        ):
            raise TypeError(
                "informed_decision must be an " "ExperienceInformedDecision"
            )

    @staticmethod
    def _validate_chain(
        *,
        evidence: ExperienceEvidence,
        assessment: EvidenceAssessment,
        support: DecisionSupportAssessment,
        policy_result: DecisionSupportPolicyResult,
        informed_decision: ExperienceInformedDecision,
    ) -> None:
        decision = informed_decision.decision

        actions = (
            evidence.action,
            assessment.action,
            support.action,
            policy_result.action,
            decision.action,
        )

        if any(action is not decision.action for action in actions):
            raise ValueError("all M5 chain actions must match")

        if assessment.evidence_strength is not evidence.strength:
            raise ValueError("assessment evidence_strength must match evidence")

        if assessment.sample_count != evidence.sample_count:
            raise ValueError("assessment sample_count must match evidence")

        if assessment.unknown_count != evidence.unknown_count:
            raise ValueError("assessment unknown_count must match evidence")

        known_count = (
            evidence.effective_count
            + evidence.degraded_count
            + evidence.ineffective_count
        )

        if assessment.known_count != known_count:
            raise ValueError("assessment known_count must match evidence")

        if support.evidence_status is not assessment.status:
            raise ValueError("support evidence_status must match assessment")

        if support.evidence_strength is not assessment.evidence_strength:
            raise ValueError("support evidence_strength must match assessment")

        if support.sample_count != assessment.sample_count:
            raise ValueError("support sample_count must match assessment")

        if support.known_count != assessment.known_count:
            raise ValueError("support known_count must match assessment")

        if support.unknown_count != assessment.unknown_count:
            raise ValueError("support unknown_count must match assessment")

        if policy_result.context_id != support.context_id:
            raise ValueError("policy_result context_id must match support")

        if policy_result.correlation_id != support.correlation_id:
            raise ValueError("policy_result correlation_id must match support")

        if policy_result.support_status is not support.support_status:
            raise ValueError("policy_result support_status must match support")

        if policy_result.evidence_status is not support.evidence_status:
            raise ValueError("policy_result evidence_status must match support")

        if policy_result.evidence_strength is not support.evidence_strength:
            raise ValueError("policy_result evidence_strength must match support")

        if decision.context_id != support.context_id:
            raise ValueError("decision context_id must match support")

        if decision.correlation_id != support.correlation_id:
            raise ValueError("decision correlation_id must match support")

        if informed_decision.policy_result != policy_result:
            raise ValueError(
                "informed_decision policy_result must match " "policy_result"
            )

        if (
            informed_decision.historical_influence_applied
            is not policy_result.historical_influence_allowed
        ):
            raise ValueError("historical influence must match policy result")


__all__ = [
    "DecisionExplanation",
    "DecisionExplanationBuilder",
]
