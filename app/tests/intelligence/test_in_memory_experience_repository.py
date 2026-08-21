"""Tests for the V10 in-memory experience repository."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    EffectivenessDimension,
    EffectivenessStatus,
    ExperienceRepository,
    FeedbackSignal,
    InMemoryExperienceRepository,
    NormalizedDecisionExperience,
    TaskAction,
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


def test_in_memory_repository_satisfies_protocol() -> None:
    repository = InMemoryExperienceRepository()

    assert isinstance(
        repository,
        ExperienceRepository,
    )


def test_repository_starts_empty() -> None:
    repository = InMemoryExperienceRepository()

    assert repository.list_all() == ()


def test_add_and_get_experience() -> None:
    repository = InMemoryExperienceRepository()

    experience = make_experience()

    repository.add(experience)

    result = repository.get(
        context_id=experience.context_id,
        correlation_id=experience.correlation_id,
        execution_id=experience.execution_id,
    )

    assert result is experience


def test_missing_experience_returns_none() -> None:
    repository = InMemoryExperienceRepository()

    result = repository.get(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="missing",
    )

    assert result is None


def test_add_rejects_invalid_experience() -> None:
    repository = InMemoryExperienceRepository()

    with pytest.raises(
        TypeError,
        match=("experience must be a " "NormalizedDecisionExperience"),
    ):
        repository.add("invalid")


def test_duplicate_provenance_is_rejected() -> None:
    repository = InMemoryExperienceRepository()

    experience = make_experience()

    repository.add(experience)

    duplicate = make_experience(
        context_id=experience.context_id,
        correlation_id=experience.correlation_id,
        execution_id=experience.execution_id,
    )

    with pytest.raises(
        ValueError,
        match="experience provenance already exists",
    ):
        repository.add(duplicate)


def test_duplicate_add_does_not_overwrite_original() -> None:
    repository = InMemoryExperienceRepository()

    original = make_experience(
        confidence=0.7,
    )

    repository.add(original)

    duplicate = make_experience(
        context_id=original.context_id,
        correlation_id=original.correlation_id,
        execution_id=original.execution_id,
        confidence=0.9,
    )

    with pytest.raises(ValueError):
        repository.add(duplicate)

    stored = repository.get(
        context_id=original.context_id,
        correlation_id=original.correlation_id,
        execution_id=original.execution_id,
    )

    assert stored is original
    assert stored.decision_confidence == 0.7


def test_find_by_comparison_key_returns_exact_match() -> None:
    repository = InMemoryExperienceRepository()

    experience = make_experience()

    repository.add(experience)

    assert repository.find_by_comparison_key(experience.comparison_key) == (experience,)


def test_semantically_equal_experiences_are_grouped() -> None:
    repository = InMemoryExperienceRepository()

    first = make_experience(
        execution_id="execution-A",
    )
    second = make_experience(
        execution_id="execution-B",
    )

    assert first.comparison_key == second.comparison_key

    repository.add(first)
    repository.add(second)

    assert repository.find_by_comparison_key(first.comparison_key) == (
        first,
        second,
    )


def test_different_semantics_are_not_grouped() -> None:
    repository = InMemoryExperienceRepository()

    effective = make_experience(
        execution_id="execution-effective",
    )

    degraded = make_experience(
        execution_id="execution-degraded",
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        ),
        status=EffectivenessStatus.DEGRADED,
        dimensions=(
            (
                EffectivenessDimension.OUTCOME,
                EffectivenessStatus.EFFECTIVE,
            ),
            (
                EffectivenessDimension.RELIABILITY,
                EffectivenessStatus.DEGRADED,
            ),
        ),
    )

    repository.add(effective)
    repository.add(degraded)

    assert repository.find_by_comparison_key(effective.comparison_key) == (effective,)

    assert repository.find_by_comparison_key(degraded.comparison_key) == (degraded,)


def test_missing_comparison_key_returns_empty_tuple() -> None:
    repository = InMemoryExperienceRepository()

    experience = make_experience()

    assert repository.find_by_comparison_key(experience.comparison_key) == ()


def test_find_returns_immutable_tuple() -> None:
    repository = InMemoryExperienceRepository()

    experience = make_experience()
    repository.add(experience)

    result = repository.find_by_comparison_key(experience.comparison_key)

    assert isinstance(result, tuple)


def test_list_all_preserves_insertion_order() -> None:
    repository = InMemoryExperienceRepository()

    first = make_experience(
        execution_id="execution-1",
    )
    second = make_experience(
        execution_id="execution-2",
    )
    third = make_experience(
        execution_id="execution-3",
    )

    repository.add(first)
    repository.add(second)
    repository.add(third)

    assert repository.list_all() == (
        first,
        second,
        third,
    )


def test_list_all_returns_tuple() -> None:
    repository = InMemoryExperienceRepository()

    repository.add(make_experience())

    assert isinstance(repository.list_all(), tuple)


def test_repository_does_not_mutate_experience() -> None:
    repository = InMemoryExperienceRepository()

    experience = make_experience()
    before = experience

    repository.add(experience)

    assert experience == before


def test_context_id_validation() -> None:
    repository = InMemoryExperienceRepository()

    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        repository.get(
            context_id="invalid",
            correlation_id=uuid4(),
            execution_id="execution-001",
        )


def test_correlation_id_validation() -> None:
    repository = InMemoryExperienceRepository()

    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        repository.get(
            context_id=uuid4(),
            correlation_id="invalid",
            execution_id="execution-001",
        )


def test_execution_id_validation() -> None:
    repository = InMemoryExperienceRepository()

    with pytest.raises(
        TypeError,
        match="execution_id must be a string",
    ):
        repository.get(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id=123,
        )


def test_empty_execution_id_is_rejected() -> None:
    repository = InMemoryExperienceRepository()

    with pytest.raises(
        ValueError,
        match="execution_id must not be empty",
    ):
        repository.get(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="",
        )


def test_comparison_key_must_be_tuple() -> None:
    repository = InMemoryExperienceRepository()

    with pytest.raises(
        TypeError,
        match="comparison_key must be a tuple",
    ):
        repository.find_by_comparison_key("invalid")


def test_repository_has_no_similarity_interface() -> None:
    repository = InMemoryExperienceRepository()

    forbidden = {
        "similarity",
        "similarity_search",
        "nearest",
        "embed",
        "vector_search",
    }

    public_names = {name for name in dir(repository) if not name.startswith("_")}

    assert not (forbidden & public_names)


def test_repository_has_no_mutation_interface() -> None:
    repository = InMemoryExperienceRepository()

    forbidden = {
        "update",
        "delete",
        "remove",
        "replace",
        "clear",
    }

    public_names = {name for name in dir(repository) if not name.startswith("_")}

    assert not (forbidden & public_names)


def test_repository_exposes_only_boundary_operations() -> None:
    repository = InMemoryExperienceRepository()

    public_names = {name for name in dir(repository) if not name.startswith("_")}

    assert public_names == {
        "add",
        "find_by_comparison_key",
        "get",
        "list_all",
    }


def test_repository_behavior_is_deterministic() -> None:
    repository = InMemoryExperienceRepository()

    first = make_experience(
        execution_id="execution-A",
    )
    second = make_experience(
        execution_id="execution-B",
    )

    repository.add(first)
    repository.add(second)

    first_lookup = repository.find_by_comparison_key(first.comparison_key)
    second_lookup = repository.find_by_comparison_key(first.comparison_key)

    assert first_lookup == second_lookup
    assert first_lookup == (
        first,
        second,
    )
