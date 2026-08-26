"""
V10 M10 capability manifest and release contract.

Defines the immutable capability boundary for the V10 bounded
intelligence architecture.

M10.1 is declarative only. It does not execute intelligence behavior,
evaluate runtime state, modify policy, or provide execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class V10ArchitectureStatus(str, Enum):
    """Architecture state represented by the V10 release manifest."""

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True, slots=True)
class V10MilestoneCapability:
    """Immutable capability declaration for one V10 milestone."""

    milestone_id: str
    name: str
    capabilities: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.milestone_id, str):
            raise TypeError("milestone_id must be a string")

        if not self.milestone_id:
            raise ValueError("milestone_id must not be empty")

        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not self.name:
            raise ValueError("name must not be empty")

        if not isinstance(self.capabilities, tuple):
            raise TypeError("capabilities must be a tuple")

        if not self.capabilities:
            raise ValueError("capabilities must not be empty")

        for capability in self.capabilities:
            if not isinstance(capability, str):
                raise TypeError("capabilities must contain strings")

            if not capability:
                raise ValueError("capabilities must not contain empty values")


@dataclass(frozen=True, slots=True)
class V10CapabilityManifest:
    """Immutable release boundary for V10 intelligence architecture."""

    version: str
    architecture_status: V10ArchitectureStatus
    feature_frozen: bool
    milestones: tuple[V10MilestoneCapability, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.version, str):
            raise TypeError("version must be a string")

        if self.version != "10.0.0":
            raise ValueError("version must be 10.0.0")

        if not isinstance(
            self.architecture_status,
            V10ArchitectureStatus,
        ):
            raise TypeError("architecture_status must be a " "V10ArchitectureStatus")

        if not isinstance(self.feature_frozen, bool):
            raise TypeError("feature_frozen must be a bool")

        if not isinstance(self.milestones, tuple):
            raise TypeError("milestones must be a tuple")

        for milestone in self.milestones:
            if not isinstance(
                milestone,
                V10MilestoneCapability,
            ):
                raise TypeError(
                    "milestones must contain " "V10MilestoneCapability values"
                )

        milestone_ids = tuple(milestone.milestone_id for milestone in self.milestones)

        if len(milestone_ids) != len(set(milestone_ids)):
            raise ValueError("milestone IDs must be unique")

    @property
    def milestone_ids(self) -> tuple[str, ...]:
        """Return manifest milestone IDs in declaration order."""

        return tuple(milestone.milestone_id for milestone in self.milestones)

    @property
    def capability_count(self) -> int:
        """Return the number of declared V10 capabilities."""

        return sum(len(milestone.capabilities) for milestone in self.milestones)


class CanonicalV10CapabilityManifest:
    """Factory for the canonical immutable V10 release manifest."""

    @staticmethod
    def build() -> V10CapabilityManifest:
        """Build the canonical M1-M9 V10 capability manifest."""

        return V10CapabilityManifest(
            version="10.0.0",
            architecture_status=(V10ArchitectureStatus.COMPLETE),
            feature_frozen=True,
            milestones=(
                V10MilestoneCapability(
                    milestone_id="M1",
                    name="Intelligence Foundation",
                    capabilities=(
                        "task decision contract",
                        "planner plan contract",
                        "planner handoff boundary",
                        "planner outcome contract",
                        "execution observation contract",
                    ),
                ),
                V10MilestoneCapability(
                    milestone_id="M2",
                    name="Decision Layer and Handoff Policies",
                    capabilities=(
                        "decision boundary",
                        "strategy handoff policy",
                        "planner outcome feedback boundary",
                        "intelligence-to-execution boundary",
                    ),
                ),
                V10MilestoneCapability(
                    milestone_id="M3",
                    name="Runtime Observation and Evaluation",
                    capabilities=(
                        "runtime observation adapter",
                        "evaluation boundary",
                        "execution feedback contract",
                        "execution feedback boundary",
                    ),
                ),
                V10MilestoneCapability(
                    milestone_id="M4",
                    name="Effectiveness and Experience Learning",
                    capabilities=(
                        "decision effectiveness",
                        "effectiveness evaluation",
                        "decision experience",
                        "experience normalization",
                        "experience repository",
                        "feedback-to-experience pipeline",
                        "experience learning",
                    ),
                ),
                V10MilestoneCapability(
                    milestone_id="M5",
                    name="Experience-Informed Decision Support",
                    capabilities=(
                        "experience evidence",
                        "evidence evaluation",
                        "decision support contract",
                        "bounded decision support policy",
                        "experience-informed decision boundary",
                        "decision explainability and provenance",
                    ),
                ),
                V10MilestoneCapability(
                    milestone_id="M6",
                    name="Controlled Adaptive Intelligence Policy",
                    capabilities=(
                        "adaptation eligibility",
                        "adaptation eligibility evaluation",
                        "adaptation decision",
                        "adaptive intelligence policy",
                        "adaptation explainability and provenance",
                        "adaptive policy composition",
                    ),
                ),
                V10MilestoneCapability(
                    milestone_id="M7",
                    name="Intelligence Orchestration Integration",
                    capabilities=(
                        "orchestration directive",
                        "orchestration translation policy",
                        "orchestration directive guard",
                        "intelligence orchestration handoff",
                        "execution integration",
                        "integration explainability",
                    ),
                ),
                V10MilestoneCapability(
                    milestone_id="M8",
                    name="Intelligence Observability and Explainability",
                    capabilities=(
                        "intelligence trace",
                        "intelligence trace builder",
                        "observability summary",
                        "observability evaluation",
                        "observability diagnostic event",
                        "explainability integration safety",
                    ),
                ),
                V10MilestoneCapability(
                    milestone_id="M9",
                    name="Intelligence Hardening and Evaluation",
                    capabilities=(
                        "intelligence invariants",
                        "invariant evaluation",
                        "canonical lifecycle scenarios",
                        "lifecycle scenario evaluation",
                        "boundary stress evaluation",
                        "hardening certification report",
                    ),
                ),
            ),
        )


__all__ = [
    "CanonicalV10CapabilityManifest",
    "V10ArchitectureStatus",
    "V10CapabilityManifest",
    "V10MilestoneCapability",
]
