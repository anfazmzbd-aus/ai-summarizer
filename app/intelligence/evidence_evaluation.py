"""
V10 deterministic experience evidence evaluation.

Interprets ExperienceEvidence into a normalized historical evidence
assessment.

M5.2 performs interpretation only. It does not recommend actions,
modify decisions, apply policy, or interact with runtime/providers.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .experience_evidence import (
    EvidenceStrength,
    ExperienceEvidence,
)
from .task_decision import TaskAction


class EvidenceAssessmentStatus(str, Enum):
    """Normalized interpretation of historical execution evidence."""

    NO_EVIDENCE = "no_evidence"
    INSUFFICIENT = "insufficient"
    MIXED = "mixed"
    SUPPORTIVE = "supportive"
    CAUTIONARY = "cautionary"
    ADVERSE = "adverse"


@dataclass(frozen=True, slots=True)
class EvidenceAssessment:
    """Immutable interpretation of one ExperienceEvidence contract."""

    action: TaskAction
    evidence_strength: EvidenceStrength

    status: EvidenceAssessmentStatus

    sample_count: int
    known_count: int
    unknown_count: int

    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(
            self.evidence_strength,
            EvidenceStrength,
        ):
            raise TypeError("evidence_strength must be an EvidenceStrength")

        if not isinstance(
            self.status,
            EvidenceAssessmentStatus,
        ):
            raise TypeError("status must be an EvidenceAssessmentStatus")

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

    @classmethod
    def create(
        cls,
        *,
        action: TaskAction,
        evidence_strength: EvidenceStrength,
        status: EvidenceAssessmentStatus,
        sample_count: int,
        known_count: int,
        unknown_count: int,
        reasons: tuple[str, ...],
    ) -> "EvidenceAssessment":
        """Create an immutable evidence assessment."""

        return cls(
            action=action,
            evidence_strength=evidence_strength,
            status=status,
            sample_count=sample_count,
            known_count=known_count,
            unknown_count=unknown_count,
            reasons=reasons,
        )


class ExperienceEvidenceEvaluator:
    """Deterministically interpret historical experience evidence."""

    def evaluate(
        self,
        evidence: ExperienceEvidence,
    ) -> EvidenceAssessment:
        """Evaluate historical evidence without producing a recommendation."""

        if not isinstance(evidence, ExperienceEvidence):
            raise TypeError("evidence must be an ExperienceEvidence")

        known_count = (
            evidence.effective_count
            + evidence.degraded_count
            + evidence.ineffective_count
        )

        status = self._derive_status(
            evidence=evidence,
            known_count=known_count,
        )

        reasons = self._build_reasons(
            evidence=evidence,
            known_count=known_count,
            status=status,
        )

        return EvidenceAssessment.create(
            action=evidence.action,
            evidence_strength=evidence.strength,
            status=status,
            sample_count=evidence.sample_count,
            known_count=known_count,
            unknown_count=evidence.unknown_count,
            reasons=reasons,
        )

    @staticmethod
    def _derive_status(
        *,
        evidence: ExperienceEvidence,
        known_count: int,
    ) -> EvidenceAssessmentStatus:
        if evidence.strength is EvidenceStrength.NONE:
            return EvidenceAssessmentStatus.NO_EVIDENCE

        if evidence.strength is EvidenceStrength.LIMITED:
            return EvidenceAssessmentStatus.INSUFFICIENT

        if known_count < 3:
            return EvidenceAssessmentStatus.INSUFFICIENT

        effective = evidence.effective_count
        degraded = evidence.degraded_count
        ineffective = evidence.ineffective_count

        if effective > degraded + ineffective:
            return EvidenceAssessmentStatus.SUPPORTIVE

        if ineffective > effective + degraded:
            return EvidenceAssessmentStatus.ADVERSE

        if degraded + ineffective > effective:
            return EvidenceAssessmentStatus.CAUTIONARY

        return EvidenceAssessmentStatus.MIXED

    @staticmethod
    def _build_reasons(
        *,
        evidence: ExperienceEvidence,
        known_count: int,
        status: EvidenceAssessmentStatus,
    ) -> tuple[str, ...]:
        reasons: list[str] = []

        if status is EvidenceAssessmentStatus.NO_EVIDENCE:
            reasons.append("no historical experience is available")

        elif status is EvidenceAssessmentStatus.INSUFFICIENT:
            if evidence.sample_count < 3:
                reasons.append("historical sample size is limited")
            else:
                reasons.append("too few historical outcomes are known")

        elif status is EvidenceAssessmentStatus.SUPPORTIVE:
            reasons.append(
                "effective historical outcomes exceed "
                "degraded and ineffective outcomes combined"
            )

        elif status is EvidenceAssessmentStatus.ADVERSE:
            reasons.append(
                "ineffective historical outcomes exceed "
                "effective and degraded outcomes combined"
            )

        elif status is EvidenceAssessmentStatus.CAUTIONARY:
            reasons.append(
                "degraded and ineffective historical outcomes "
                "exceed effective outcomes"
            )

        else:
            reasons.append("historical outcomes provide mixed evidence")

        if evidence.unknown_count > 0:
            reasons.append(f"{evidence.unknown_count} historical outcomes are unknown")

        if known_count > 0:
            reasons.append(f"{known_count} historical outcomes are known")

        return tuple(reasons)


__all__ = [
    "EvidenceAssessment",
    "EvidenceAssessmentStatus",
    "ExperienceEvidenceEvaluator",
]
