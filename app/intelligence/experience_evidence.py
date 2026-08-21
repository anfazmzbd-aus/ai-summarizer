"""
V10 experience evidence contracts.

Transforms historical learning context into a compact, immutable,
provider-independent evidence representation.

M5.1 describes the amount and distribution of historical evidence only.
It does not recommend actions, modify decisions, or apply adaptive policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .experience_learning import ExperienceLearningContext
from .task_decision import TaskAction


class EvidenceStrength(str, Enum):
    """Amount of historical evidence available."""

    NONE = "none"
    LIMITED = "limited"
    ESTABLISHED = "established"


@dataclass(frozen=True, slots=True)
class ExperienceEvidence:
    """Immutable historical evidence summary for one task action."""

    action: TaskAction

    sample_count: int

    effective_count: int
    degraded_count: int
    ineffective_count: int
    unknown_count: int

    strength: EvidenceStrength

    def __post_init__(self) -> None:
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

        if not isinstance(self.strength, EvidenceStrength):
            raise TypeError("strength must be an EvidenceStrength")

        expected_strength = self._expected_strength(self.sample_count)

        if self.strength is not expected_strength:
            raise ValueError("strength must match sample_count")

    @staticmethod
    def _expected_strength(
        sample_count: int,
    ) -> EvidenceStrength:
        if sample_count == 0:
            return EvidenceStrength.NONE

        if sample_count <= 2:
            return EvidenceStrength.LIMITED

        return EvidenceStrength.ESTABLISHED

    @classmethod
    def create(
        cls,
        *,
        action: TaskAction,
        sample_count: int,
        effective_count: int,
        degraded_count: int,
        ineffective_count: int,
        unknown_count: int,
    ) -> "ExperienceEvidence":
        """Create evidence with deterministically derived strength."""

        if not isinstance(sample_count, int) or isinstance(
            sample_count,
            bool,
        ):
            raise TypeError("sample_count must be an integer")

        if sample_count < 0:
            raise ValueError("sample_count must be greater than or equal to 0")

        return cls(
            action=action,
            sample_count=sample_count,
            effective_count=effective_count,
            degraded_count=degraded_count,
            ineffective_count=ineffective_count,
            unknown_count=unknown_count,
            strength=cls._expected_strength(sample_count),
        )


class ExperienceEvidenceBuilder:
    """Build deterministic evidence from historical learning context."""

    def build(
        self,
        context: ExperienceLearningContext,
    ) -> ExperienceEvidence:
        """Convert learning context into immutable evidence."""

        if not isinstance(
            context,
            ExperienceLearningContext,
        ):
            raise TypeError("context must be an ExperienceLearningContext")

        return ExperienceEvidence.create(
            action=context.action,
            sample_count=context.total_count,
            effective_count=context.effective_count,
            degraded_count=context.degraded_count,
            ineffective_count=context.ineffective_count,
            unknown_count=context.unknown_count,
        )


__all__ = [
    "EvidenceStrength",
    "ExperienceEvidence",
    "ExperienceEvidenceBuilder",
]
