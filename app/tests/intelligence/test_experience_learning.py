"""Tests for the V10 experience learning consumption boundary."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    EffectivenessDimension,
    EffectivenessStatus,
    ExperienceLearningContext,
    ExperienceRepository,
    FeedbackSignal,
    InMemoryExperienceRepository,
    LearningExperienceConsumer,
    NormalizedDecisionExperience,
    TaskAction,
)


def make_experience(
    *,
    execution_id: str,
    action: TaskAction = TaskAction.SUMMARIZE,
    status: EffectivenessStatus = (EffectivenessStatus.EFFECTIVE),
) -> NormalizedDecisionExperience:
    return NormalizedDecisionExperience(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id=execution_id,
        action=action,
        decision_confidence=0.8,
        feedback_signals=(FeedbackSignal.SUCCESS,),
        effectiveness_status=status,
        effectiveness_dimensions=(
            (
                EffectivenessDimension.OUTCOME,
                (
                    EffectivenessStatus.EFFECTIVE
                    if status is not EffectivenessStatus.INEFFECTIVE
                    else EffectivenessStatus.INEFFECTIVE
                ),
            ),
        ),
    )


def make_repository(
    *experiences: NormalizedDecisionExperience,
) -> InMemoryExperienceRepository:
    repository = InMemoryExperienceRepository()

    for experience in experiences:
        repository.add(experience)

    return repository


def test_consumer_returns_learning_context() -> None:
    repository = make_repository(
        make_experience(
            execution_id="execution-001",
        )
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert isinstance(
        result,
        ExperienceLearningContext,
    )


def test_empty_repository_returns_empty_context() -> None:
    repository = InMemoryExperienceRepository()

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.action is TaskAction.SUMMARIZE
    assert result.experiences == ()
    assert result.total_count == 0
    assert result.effective_count == 0
    assert result.degraded_count == 0
    assert result.ineffective_count == 0
    assert result.unknown_count == 0


def test_consumer_filters_by_action() -> None:
    summarize = make_experience(
        execution_id="summarize-001",
        action=TaskAction.SUMMARIZE,
    )

    verify = make_experience(
        execution_id="verify-001",
        action=TaskAction.VERIFY,
    )

    repository = make_repository(
        summarize,
        verify,
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.experiences == (summarize,)


def test_consumer_preserves_repository_order() -> None:
    first = make_experience(
        execution_id="execution-1",
    )
    second = make_experience(
        execution_id="execution-2",
    )
    third = make_experience(
        execution_id="execution-3",
    )

    repository = make_repository(
        first,
        second,
        third,
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.experiences == (
        first,
        second,
        third,
    )


def test_total_count_matches_matching_experiences() -> None:
    repository = make_repository(
        make_experience(
            execution_id="execution-1",
        ),
        make_experience(
            execution_id="execution-2",
        ),
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.total_count == 2


def test_effective_count_is_aggregated() -> None:
    repository = make_repository(
        make_experience(
            execution_id="execution-1",
            status=EffectivenessStatus.EFFECTIVE,
        ),
        make_experience(
            execution_id="execution-2",
            status=EffectivenessStatus.EFFECTIVE,
        ),
        make_experience(
            execution_id="execution-3",
            status=EffectivenessStatus.DEGRADED,
        ),
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.effective_count == 2


def test_degraded_count_is_aggregated() -> None:
    repository = make_repository(
        make_experience(
            execution_id="execution-1",
            status=EffectivenessStatus.DEGRADED,
        ),
        make_experience(
            execution_id="execution-2",
            status=EffectivenessStatus.EFFECTIVE,
        ),
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.degraded_count == 1


def test_ineffective_count_is_aggregated() -> None:
    repository = make_repository(
        make_experience(
            execution_id="execution-1",
            status=EffectivenessStatus.INEFFECTIVE,
        ),
        make_experience(
            execution_id="execution-2",
            status=EffectivenessStatus.EFFECTIVE,
        ),
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.ineffective_count == 1


def test_unknown_count_is_aggregated() -> None:
    repository = make_repository(
        make_experience(
            execution_id="execution-1",
            status=EffectivenessStatus.UNKNOWN,
        ),
        make_experience(
            execution_id="execution-2",
            status=EffectivenessStatus.EFFECTIVE,
        ),
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.unknown_count == 1


def test_all_effectiveness_counts_are_aggregated() -> None:
    repository = make_repository(
        make_experience(
            execution_id="effective",
            status=EffectivenessStatus.EFFECTIVE,
        ),
        make_experience(
            execution_id="degraded",
            status=EffectivenessStatus.DEGRADED,
        ),
        make_experience(
            execution_id="ineffective",
            status=EffectivenessStatus.INEFFECTIVE,
        ),
        make_experience(
            execution_id="unknown",
            status=EffectivenessStatus.UNKNOWN,
        ),
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.total_count == 4
    assert result.effective_count == 1
    assert result.degraded_count == 1
    assert result.ineffective_count == 1
    assert result.unknown_count == 1


def test_non_matching_actions_do_not_affect_counts() -> None:
    repository = make_repository(
        make_experience(
            execution_id="summarize",
            action=TaskAction.SUMMARIZE,
            status=EffectivenessStatus.EFFECTIVE,
        ),
        make_experience(
            execution_id="verify",
            action=TaskAction.VERIFY,
            status=EffectivenessStatus.INEFFECTIVE,
        ),
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    assert result.total_count == 1
    assert result.effective_count == 1
    assert result.ineffective_count == 0


def test_consumer_rejects_invalid_action() -> None:
    repository = InMemoryExperienceRepository()

    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        LearningExperienceConsumer(
            repository=repository,
        ).consume(
            action="summarize",
        )


def test_consumer_rejects_invalid_repository() -> None:
    with pytest.raises(
        TypeError,
        match="repository must satisfy ExperienceRepository",
    ):
        LearningExperienceConsumer(
            repository=object(),
        )


def test_consumer_accepts_repository_protocol() -> None:
    repository = InMemoryExperienceRepository()

    assert isinstance(
        repository,
        ExperienceRepository,
    )

    consumer = LearningExperienceConsumer(
        repository=repository,
    )

    assert (
        consumer.consume(
            action=TaskAction.SUMMARIZE,
        ).total_count
        == 0
    )


def test_learning_context_is_frozen() -> None:
    repository = make_repository(
        make_experience(
            execution_id="execution-001",
        )
    )

    result = LearningExperienceConsumer(
        repository=repository,
    ).consume(
        action=TaskAction.SUMMARIZE,
    )

    with pytest.raises(FrozenInstanceError):
        result.total_count = 10


def test_learning_context_rejects_invalid_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        ExperienceLearningContext(
            action="summarize",
            experiences=(),
            total_count=0,
            effective_count=0,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
        )


def test_learning_context_requires_tuple_experiences() -> None:
    with pytest.raises(
        TypeError,
        match="experiences must be a tuple",
    ):
        ExperienceLearningContext(
            action=TaskAction.SUMMARIZE,
            experiences=[],
            total_count=0,
            effective_count=0,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
        )


def test_learning_context_rejects_invalid_experience() -> None:
    with pytest.raises(
        TypeError,
        match=("experiences must contain " "NormalizedDecisionExperience values"),
    ):
        ExperienceLearningContext(
            action=TaskAction.SUMMARIZE,
            experiences=("invalid",),
            total_count=1,
            effective_count=1,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
        )


def test_learning_context_rejects_wrong_action_experience() -> None:
    experience = make_experience(
        execution_id="execution-001",
        action=TaskAction.VERIFY,
    )

    with pytest.raises(
        ValueError,
        match="all experiences must match action",
    ):
        ExperienceLearningContext(
            action=TaskAction.SUMMARIZE,
            experiences=(experience,),
            total_count=1,
            effective_count=1,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "total_count",
        "effective_count",
        "degraded_count",
        "ineffective_count",
        "unknown_count",
    ],
)
def test_learning_context_counts_must_be_integers(
    field_name: str,
) -> None:
    values = {
        "action": TaskAction.SUMMARIZE,
        "experiences": (),
        "total_count": 0,
        "effective_count": 0,
        "degraded_count": 0,
        "ineffective_count": 0,
        "unknown_count": 0,
    }

    values[field_name] = 1.5

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an integer",
    ):
        ExperienceLearningContext(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "total_count",
        "effective_count",
        "degraded_count",
        "ineffective_count",
        "unknown_count",
    ],
)
def test_learning_context_counts_reject_boolean(
    field_name: str,
) -> None:
    values = {
        "action": TaskAction.SUMMARIZE,
        "experiences": (),
        "total_count": 0,
        "effective_count": 0,
        "degraded_count": 0,
        "ineffective_count": 0,
        "unknown_count": 0,
    }

    values[field_name] = True

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an integer",
    ):
        ExperienceLearningContext(**values)


def test_total_count_must_match_experience_count() -> None:
    experience = make_experience(
        execution_id="execution-001",
    )

    with pytest.raises(
        ValueError,
        match=("total_count must match number of experiences"),
    ):
        ExperienceLearningContext(
            action=TaskAction.SUMMARIZE,
            experiences=(experience,),
            total_count=2,
            effective_count=1,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
        )


def test_effectiveness_counts_must_sum_to_total() -> None:
    experience = make_experience(
        execution_id="execution-001",
    )

    with pytest.raises(
        ValueError,
        match=("effectiveness counts must sum to total_count"),
    ):
        ExperienceLearningContext(
            action=TaskAction.SUMMARIZE,
            experiences=(experience,),
            total_count=1,
            effective_count=0,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
        )


def test_learning_context_contains_no_action_recommendation() -> None:
    forbidden = {
        "recommended_action",
        "retry",
        "replan",
        "strategy",
        "provider",
        "policy",
        "reward",
    }

    assert not (forbidden & set(ExperienceLearningContext.__dataclass_fields__))


def test_consumer_has_no_adaptive_interface() -> None:
    forbidden = {
        "adapt",
        "learn",
        "replan",
        "retry",
        "execute",
        "select_strategy",
        "switch_provider",
        "recommend",
    }

    public_names = {
        name for name in dir(LearningExperienceConsumer) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_consumer_exposes_only_consume() -> None:
    public_names = {
        name for name in dir(LearningExperienceConsumer) if not name.startswith("_")
    }

    assert public_names == {"consume"}


def test_learning_consumption_is_deterministic() -> None:
    repository = make_repository(
        make_experience(
            execution_id="execution-1",
            status=EffectivenessStatus.EFFECTIVE,
        ),
        make_experience(
            execution_id="execution-2",
            status=EffectivenessStatus.DEGRADED,
        ),
    )

    consumer = LearningExperienceConsumer(
        repository=repository,
    )

    first = consumer.consume(
        action=TaskAction.SUMMARIZE,
    )
    second = consumer.consume(
        action=TaskAction.SUMMARIZE,
    )

    assert first == second
