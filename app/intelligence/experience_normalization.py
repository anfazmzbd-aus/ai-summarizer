"""
V10 decision experience normalization.

Transforms DecisionExperience into a stable, deterministic representation
suitable for comparison and future repository retrieval.

Normalization does not persist experiences, calculate similarity scores,
perform learning, or alter planning/runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias
from uuid import UUID

from .decision_effectiveness import (
    EffectivenessDimension,
    EffectivenessStatus,
)
from .decision_experience import DecisionExperience
from .execution_feedback import FeedbackSignal
from .task_decision import TaskAction


EffectivenessFeature: TypeAlias = tuple[
    EffectivenessDimension,
    EffectivenessStatus,
]

ExperienceComparisonKey: TypeAlias = tuple[
    TaskAction,
    float,
    tuple[FeedbackSignal, ...],
    EffectivenessStatus,
    tuple[EffectivenessFeature, ...],
]


@dataclass(frozen=True, slots=True)
class NormalizedDecisionExperience:
    """
    Immutable normalized representation of a DecisionExperience.

    Provenance identifies the originating execution but is deliberately
    excluded from comparison_key.

    Free-form reasons and arbitrary metadata are also deliberately excluded
    from the normalized comparison feature set.
    """

    context_id: UUID
    correlation_id: UUID
    execution_id: str

    action: TaskAction
    decision_confidence: float

    feedback_signals: tuple[FeedbackSignal, ...]

    effectiveness_status: EffectivenessStatus
    effectiveness_dimensions: tuple[EffectivenessFeature, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.execution_id, str):
            raise TypeError("execution_id must be a string")

        if not self.execution_id:
            raise ValueError("execution_id must not be empty")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(
            self.decision_confidence,
            (int, float),
        ) or isinstance(self.decision_confidence, bool):
            raise TypeError("decision_confidence must be a number")

        if not 0.0 <= float(self.decision_confidence) <= 1.0:
            raise ValueError("decision_confidence must be between 0 and 1")

        if not isinstance(self.feedback_signals, tuple):
            raise TypeError("feedback_signals must be a tuple")

        seen_signals: set[FeedbackSignal] = set()

        for signal in self.feedback_signals:
            if not isinstance(signal, FeedbackSignal):
                raise TypeError(
                    "feedback_signals must contain " "FeedbackSignal values"
                )

            if signal in seen_signals:
                raise ValueError("feedback_signals must not contain duplicates")

            seen_signals.add(signal)

        if not isinstance(
            self.effectiveness_status,
            EffectivenessStatus,
        ):
            raise TypeError("effectiveness_status must be an " "EffectivenessStatus")

        if not isinstance(
            self.effectiveness_dimensions,
            tuple,
        ):
            raise TypeError("effectiveness_dimensions must be a tuple")

        seen_dimensions: set[EffectivenessDimension] = set()

        for feature in self.effectiveness_dimensions:
            if not isinstance(feature, tuple) or len(feature) != 2:
                raise TypeError(
                    "effectiveness_dimensions entries must be "
                    "(EffectivenessDimension, EffectivenessStatus) tuples"
                )

            dimension, status = feature

            if not isinstance(
                dimension,
                EffectivenessDimension,
            ):
                raise TypeError(
                    "effectiveness dimension keys must be "
                    "EffectivenessDimension values"
                )

            if not isinstance(status, EffectivenessStatus):
                raise TypeError(
                    "effectiveness dimension values must be "
                    "EffectivenessStatus values"
                )

            if dimension in seen_dimensions:
                raise ValueError(
                    "effectiveness_dimensions must not contain " "duplicate dimensions"
                )

            seen_dimensions.add(dimension)

        object.__setattr__(
            self,
            "decision_confidence",
            float(self.decision_confidence),
        )

    @property
    def comparison_key(self) -> ExperienceComparisonKey:
        """
        Return the deterministic semantic comparison key.

        Execution provenance is deliberately excluded.
        """
        return (
            self.action,
            self.decision_confidence,
            self.feedback_signals,
            self.effectiveness_status,
            self.effectiveness_dimensions,
        )


class ExperienceNormalizer:
    """Normalize DecisionExperience into stable comparison features."""

    def normalize(
        self,
        experience: DecisionExperience,
    ) -> NormalizedDecisionExperience:
        """Return a deterministic normalized experience."""

        if not isinstance(experience, DecisionExperience):
            raise TypeError("experience must be a DecisionExperience")

        signals = tuple(
            sorted(
                experience.feedback_signals,
                key=lambda signal: signal.value,
            )
        )

        dimensions = tuple(
            sorted(
                experience.effectiveness_dimensions.items(),
                key=lambda item: item[0].value,
            )
        )

        return NormalizedDecisionExperience(
            context_id=experience.context_id,
            correlation_id=experience.correlation_id,
            execution_id=experience.execution_id,
            action=experience.action,
            decision_confidence=experience.decision_confidence,
            feedback_signals=signals,
            effectiveness_status=experience.effectiveness_status,
            effectiveness_dimensions=dimensions,
        )


__all__ = [
    "EffectivenessFeature",
    "ExperienceComparisonKey",
    "ExperienceNormalizer",
    "NormalizedDecisionExperience",
]
