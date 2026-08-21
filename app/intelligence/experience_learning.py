"""
V10 experience learning consumption boundary.

Provides deterministic, provider-independent read access to historical
normalized decision experiences.

The learning boundary exposes historical context only. It does not adapt
policies, alter planners, select providers, execute runtime actions, or
recommend decisions.
"""

from __future__ import annotations

from dataclasses import dataclass

from .decision_effectiveness import EffectivenessStatus
from .experience_normalization import NormalizedDecisionExperience
from .experience_repository import ExperienceRepository
from .task_decision import TaskAction


@dataclass(frozen=True, slots=True)
class ExperienceLearningContext:
    """
    Immutable historical experience context for one task action.

    Counts summarize the effectiveness of matching historical experiences.
    The context contains observations only and prescribes no future action.
    """

    action: TaskAction

    experiences: tuple[
        NormalizedDecisionExperience,
        ...,
    ]

    total_count: int
    effective_count: int
    degraded_count: int
    ineffective_count: int
    unknown_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(self.experiences, tuple):
            raise TypeError("experiences must be a tuple")

        for experience in self.experiences:
            if not isinstance(
                experience,
                NormalizedDecisionExperience,
            ):
                raise TypeError(
                    "experiences must contain " "NormalizedDecisionExperience values"
                )

            if experience.action is not self.action:
                raise ValueError("all experiences must match action")

        counts = {
            "total_count": self.total_count,
            "effective_count": self.effective_count,
            "degraded_count": self.degraded_count,
            "ineffective_count": self.ineffective_count,
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

        if self.total_count != len(self.experiences):
            raise ValueError("total_count must match number of experiences")

        categorized_total = (
            self.effective_count
            + self.degraded_count
            + self.ineffective_count
            + self.unknown_count
        )

        if categorized_total != self.total_count:
            raise ValueError("effectiveness counts must sum to total_count")


class LearningExperienceConsumer:
    """
    Consume historical normalized experiences as intelligence context.

    The consumer performs filtering and deterministic aggregation only.
    """

    def __init__(
        self,
        *,
        repository: ExperienceRepository,
    ) -> None:
        if not isinstance(
            repository,
            ExperienceRepository,
        ):
            raise TypeError("repository must satisfy ExperienceRepository")

        self._repository = repository

    def consume(
        self,
        *,
        action: TaskAction,
    ) -> ExperienceLearningContext:
        """
        Return deterministic historical context for one task action.
        """

        if not isinstance(action, TaskAction):
            raise TypeError("action must be a TaskAction")

        matching = tuple(
            experience
            for experience in self._repository.list_all()
            if experience.action is action
        )

        effective_count = sum(
            1
            for experience in matching
            if (experience.effectiveness_status is EffectivenessStatus.EFFECTIVE)
        )

        degraded_count = sum(
            1
            for experience in matching
            if (experience.effectiveness_status is EffectivenessStatus.DEGRADED)
        )

        ineffective_count = sum(
            1
            for experience in matching
            if (experience.effectiveness_status is EffectivenessStatus.INEFFECTIVE)
        )

        unknown_count = sum(
            1
            for experience in matching
            if (experience.effectiveness_status is EffectivenessStatus.UNKNOWN)
        )

        return ExperienceLearningContext(
            action=action,
            experiences=matching,
            total_count=len(matching),
            effective_count=effective_count,
            degraded_count=degraded_count,
            ineffective_count=ineffective_count,
            unknown_count=unknown_count,
        )


__all__ = [
    "ExperienceLearningContext",
    "LearningExperienceConsumer",
]
