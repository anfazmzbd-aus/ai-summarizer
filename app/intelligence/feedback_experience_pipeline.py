"""
V10 feedback-to-experience pipeline.

Composes the existing effectiveness, experience, normalization, and repository
boundaries into one deterministic orchestration path.

The pipeline does not execute runtime work, adapt policies, perform learning,
or select providers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .decision_effectiveness import DecisionEffectiveness
from .decision_experience import (
    DecisionExperience,
    DecisionExperienceBuilder,
)
from .effectiveness_evaluator import (
    DecisionEffectivenessEvaluator,
)
from .execution_feedback import ExecutionFeedback
from .experience_normalization import (
    ExperienceNormalizer,
    NormalizedDecisionExperience,
)
from .experience_repository import ExperienceRepository
from .task_decision import TaskDecision


@dataclass(frozen=True, slots=True)
class FeedbackExperienceResult:
    """Immutable result of one feedback-to-experience pipeline run."""

    effectiveness: DecisionEffectiveness
    experience: DecisionExperience
    normalized_experience: NormalizedDecisionExperience

    def __post_init__(self) -> None:
        if not isinstance(
            self.effectiveness,
            DecisionEffectiveness,
        ):
            raise TypeError("effectiveness must be a DecisionEffectiveness")

        if not isinstance(
            self.experience,
            DecisionExperience,
        ):
            raise TypeError("experience must be a DecisionExperience")

        if not isinstance(
            self.normalized_experience,
            NormalizedDecisionExperience,
        ):
            raise TypeError(
                "normalized_experience must be a " "NormalizedDecisionExperience"
            )

        if (
            self.effectiveness.context_id != self.experience.context_id
            or self.effectiveness.context_id != self.normalized_experience.context_id
        ):
            raise ValueError("pipeline result context_id values must match")

        if (
            self.effectiveness.correlation_id != self.experience.correlation_id
            or self.effectiveness.correlation_id
            != self.normalized_experience.correlation_id
        ):
            raise ValueError("pipeline result correlation_id values must match")

        if (
            self.effectiveness.execution_id != self.experience.execution_id
            or self.effectiveness.execution_id
            != self.normalized_experience.execution_id
        ):
            raise ValueError("pipeline result execution_id values must match")


class FeedbackExperiencePipeline:
    """
    Compose execution feedback into a persisted normalized experience.

    Existing components retain ownership of their semantics:

    - DecisionEffectivenessEvaluator evaluates effectiveness.
    - DecisionExperienceBuilder creates the audit-rich experience.
    - ExperienceNormalizer creates stable comparison features.
    - ExperienceRepository owns storage.
    """

    def __init__(
        self,
        *,
        repository: ExperienceRepository,
        evaluator: DecisionEffectivenessEvaluator | None = None,
        builder: DecisionExperienceBuilder | None = None,
        normalizer: ExperienceNormalizer | None = None,
    ) -> None:
        if not isinstance(repository, ExperienceRepository):
            raise TypeError("repository must satisfy ExperienceRepository")

        if evaluator is not None and not isinstance(
            evaluator,
            DecisionEffectivenessEvaluator,
        ):
            raise TypeError(
                "evaluator must be a " "DecisionEffectivenessEvaluator or None"
            )

        if builder is not None and not isinstance(
            builder,
            DecisionExperienceBuilder,
        ):
            raise TypeError("builder must be a DecisionExperienceBuilder or None")

        if normalizer is not None and not isinstance(
            normalizer,
            ExperienceNormalizer,
        ):
            raise TypeError("normalizer must be an ExperienceNormalizer or None")

        self._repository = repository
        self._evaluator = (
            evaluator if evaluator is not None else DecisionEffectivenessEvaluator()
        )
        self._builder = builder if builder is not None else DecisionExperienceBuilder()
        self._normalizer = (
            normalizer if normalizer is not None else ExperienceNormalizer()
        )

    def process(
        self,
        decision: TaskDecision,
        feedback: ExecutionFeedback,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> FeedbackExperienceResult:
        """
        Evaluate, build, normalize, and store one completed decision cycle.
        """

        if not isinstance(decision, TaskDecision):
            raise TypeError("decision must be a TaskDecision")

        if not isinstance(feedback, ExecutionFeedback):
            raise TypeError("feedback must be an ExecutionFeedback")

        if metadata is not None and not isinstance(
            metadata,
            Mapping,
        ):
            raise TypeError("metadata must be a mapping or None")

        effectiveness = self._evaluator.evaluate(
            decision,
            feedback,
        )

        experience = self._builder.build(
            decision,
            feedback,
            effectiveness,
            metadata=metadata,
        )

        normalized = self._normalizer.normalize(
            experience,
        )

        self._repository.add(normalized)

        return FeedbackExperienceResult(
            effectiveness=effectiveness,
            experience=experience,
            normalized_experience=normalized,
        )


__all__ = [
    "FeedbackExperiencePipeline",
    "FeedbackExperienceResult",
]
