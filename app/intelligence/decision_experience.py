"""
V10 decision experience contracts.

Defines the immutable, provider-independent representation of a completed
intelligence decision cycle.

A decision experience captures normalized decision, execution-feedback,
and effectiveness information. It does not persist itself, adapt policies,
modify runtime state, or invoke external providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID

from .decision_effectiveness import (
    DecisionEffectiveness,
    EffectivenessDimension,
    EffectivenessStatus,
)
from .execution_feedback import ExecutionFeedback, FeedbackSignal
from .task_decision import TaskAction, TaskDecision


@dataclass(frozen=True, slots=True)
class DecisionExperience:
    """Immutable normalized representation of one completed decision cycle."""

    context_id: UUID
    correlation_id: UUID
    execution_id: str

    action: TaskAction
    decision_reason: str
    decision_confidence: float

    feedback_signals: tuple[FeedbackSignal, ...]

    effectiveness_status: EffectivenessStatus
    effectiveness_dimensions: Mapping[
        EffectivenessDimension,
        EffectivenessStatus,
    ]

    reasons: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

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

        if not isinstance(self.decision_reason, str):
            raise TypeError("decision_reason must be a string")

        if not self.decision_reason:
            raise ValueError("decision_reason must not be empty")

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
            Mapping,
        ):
            raise TypeError("effectiveness_dimensions must be a mapping")

        normalized_dimensions: dict[
            EffectivenessDimension,
            EffectivenessStatus,
        ] = {}

        for dimension, status in self.effectiveness_dimensions.items():
            if not isinstance(
                dimension,
                EffectivenessDimension,
            ):
                raise TypeError(
                    "effectiveness dimension keys must be "
                    "EffectivenessDimension values"
                )

            if not isinstance(
                status,
                EffectivenessStatus,
            ):
                raise TypeError(
                    "effectiveness dimension values must be "
                    "EffectivenessStatus values"
                )

            normalized_dimensions[dimension] = status

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(
            self,
            "decision_confidence",
            float(self.decision_confidence),
        )

        object.__setattr__(
            self,
            "effectiveness_dimensions",
            MappingProxyType(normalized_dimensions),
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @classmethod
    def create(
        cls,
        *,
        context_id: UUID,
        correlation_id: UUID,
        execution_id: str,
        action: TaskAction,
        decision_reason: str,
        decision_confidence: float,
        feedback_signals: tuple[FeedbackSignal, ...],
        effectiveness_status: EffectivenessStatus,
        effectiveness_dimensions: Mapping[
            EffectivenessDimension,
            EffectivenessStatus,
        ],
        reasons: tuple[str, ...] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> "DecisionExperience":
        """Create an immutable decision experience."""

        return cls(
            context_id=context_id,
            correlation_id=correlation_id,
            execution_id=execution_id,
            action=action,
            decision_reason=decision_reason,
            decision_confidence=decision_confidence,
            feedback_signals=feedback_signals,
            effectiveness_status=effectiveness_status,
            effectiveness_dimensions=effectiveness_dimensions,
            reasons=reasons,
            metadata={} if metadata is None else metadata,
        )


class DecisionExperienceBuilder:
    """Build deterministic decision experiences from normalized contracts."""

    def build(
        self,
        decision: TaskDecision,
        feedback: ExecutionFeedback,
        effectiveness: DecisionEffectiveness,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> DecisionExperience:
        """Build one normalized experience from a completed decision cycle."""

        self._validate_inputs(
            decision,
            feedback,
            effectiveness,
        )

        return DecisionExperience.create(
            context_id=decision.context_id,
            correlation_id=decision.correlation_id,
            execution_id=feedback.execution_id,
            action=decision.action,
            decision_reason=decision.reason,
            decision_confidence=decision.confidence,
            feedback_signals=feedback.signals,
            effectiveness_status=effectiveness.status,
            effectiveness_dimensions=effectiveness.dimensions,
            reasons=effectiveness.reasons,
            metadata={} if metadata is None else metadata,
        )

    @staticmethod
    def _validate_inputs(
        decision: TaskDecision,
        feedback: ExecutionFeedback,
        effectiveness: DecisionEffectiveness,
    ) -> None:
        if not isinstance(decision, TaskDecision):
            raise TypeError("decision must be a TaskDecision")

        if not isinstance(feedback, ExecutionFeedback):
            raise TypeError("feedback must be an ExecutionFeedback")

        if not isinstance(
            effectiveness,
            DecisionEffectiveness,
        ):
            raise TypeError("effectiveness must be a " "DecisionEffectiveness")

        if decision.context_id != feedback.context_id:
            raise ValueError("decision and feedback context_id must match")

        if decision.context_id != effectiveness.context_id:
            raise ValueError("decision and effectiveness context_id " "must match")

        if feedback.context_id != effectiveness.context_id:
            raise ValueError("feedback and effectiveness context_id " "must match")

        if decision.correlation_id != feedback.correlation_id:
            raise ValueError("decision and feedback correlation_id " "must match")

        if decision.correlation_id != effectiveness.correlation_id:
            raise ValueError("decision and effectiveness correlation_id " "must match")

        if feedback.correlation_id != effectiveness.correlation_id:
            raise ValueError("feedback and effectiveness correlation_id " "must match")

        if feedback.execution_id != effectiveness.execution_id:
            raise ValueError("feedback and effectiveness execution_id " "must match")


__all__ = [
    "DecisionExperience",
    "DecisionExperienceBuilder",
]
