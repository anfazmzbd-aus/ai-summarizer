"""Tests for the V10 experience repository boundary."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    EffectivenessDimension,
    EffectivenessStatus,
    ExperienceRepository,
    FeedbackSignal,
    NormalizedDecisionExperience,
    TaskAction,
    experience_provenance_key,
)


def make_experience(
    *,
    context_id=None,
    correlation_id=None,
    execution_id: str = "execution-001",
    action: TaskAction = TaskAction.SUMMARIZE,
    confidence: float = 0.8,
    signals: tuple[FeedbackSignal, ...] = (FeedbackSignal.SUCCESS,),
    status: EffectivenessStatus = (EffectivenessStatus.EFFECTIVE),
    dimensions=None,
) -> NormalizedDecisionExperience:
    return NormalizedDecisionExperience(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        execution_id=execution_id,
        action=action,
        decision_confidence=confidence,
        feedback_signals=signals,
        effectiveness_status=status,
        effectiveness_dimensions=(
            (
                (
                    EffectivenessDimension.OUTCOME,
                    EffectivenessStatus.EFFECTIVE,
                ),
            )
            if dimensions is None
            else dimensions
        ),
    )


def test_repository_is_runtime_checkable_protocol() -> None:
    class Repository:
        def add(self, experience):
            pass

        def get(
            self,
            *,
            context_id,
            correlation_id,
            execution_id,
        ):
            return None

        def find_by_comparison_key(
            self,
            comparison_key,
        ):
            return ()

        def list_all(self):
            return ()

    assert isinstance(Repository(), ExperienceRepository)


def test_repository_protocol_requires_expected_interface() -> None:
    class IncompleteRepository:
        def add(self, experience):
            pass

    assert not isinstance(
        IncompleteRepository(),
        ExperienceRepository,
    )


def test_experience_provenance_key() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    experience = make_experience(
        context_id=context_id,
        correlation_id=correlation_id,
        execution_id="execution-special",
    )

    assert experience_provenance_key(experience) == (
        context_id,
        correlation_id,
        "execution-special",
    )


def test_provenance_key_rejects_invalid_experience() -> None:
    with pytest.raises(
        TypeError,
        match=("experience must be a " "NormalizedDecisionExperience"),
    ):
        experience_provenance_key("invalid")


def test_repository_boundary_contains_no_backend_api() -> None:
    forbidden = {
        "connect",
        "commit",
        "rollback",
        "execute_sql",
        "embed",
        "similarity_search",
        "redis",
        "sqlite",
    }

    public_names = {
        name for name in dir(ExperienceRepository) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_repository_boundary_is_minimal() -> None:
    public_names = {
        name for name in dir(ExperienceRepository) if not name.startswith("_")
    }

    assert public_names == {
        "add",
        "find_by_comparison_key",
        "get",
        "list_all",
    }
