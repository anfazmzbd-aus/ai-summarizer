"""Tests for V10 M7 orchestration directive contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationDisposition,
    OrchestrationDirective,
    OrchestrationDisposition,
    TaskAction,
)


def make_directive(
    *,
    adaptation_disposition: AdaptationDisposition = (AdaptationDisposition.ADVISORY),
    orchestration_disposition: OrchestrationDisposition = (
        OrchestrationDisposition.ADVISORY_CONTEXT
    ),
    execution_change_allowed: bool = False,
    review_required: bool = False,
    reasons: tuple[str, ...] = ("directive reason",),
) -> OrchestrationDirective:
    return OrchestrationDirective.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        adaptation_disposition=adaptation_disposition,
        orchestration_disposition=orchestration_disposition,
        execution_change_allowed=execution_change_allowed,
        review_required=review_required,
        reasons=reasons,
    )


def test_orchestration_disposition_values_are_stable() -> None:
    assert OrchestrationDisposition.NO_CHANGE.value == "no_change"
    assert OrchestrationDisposition.ADVISORY_CONTEXT.value == "advisory_context"
    assert OrchestrationDisposition.BOUNDED_CONSTRAINT.value == "bounded_constraint"
    assert OrchestrationDisposition.REVIEW_REQUIRED.value == "review_required"


def test_create_returns_directive() -> None:
    result = make_directive()

    assert isinstance(result, OrchestrationDirective)


def test_context_id_is_preserved() -> None:
    context_id = uuid4()

    result = OrchestrationDirective.create(
        context_id=context_id,
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        adaptation_disposition=AdaptationDisposition.PRESERVE,
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
        reasons=(),
    )

    assert result.context_id == context_id


def test_correlation_id_is_preserved() -> None:
    correlation_id = uuid4()

    result = OrchestrationDirective.create(
        context_id=uuid4(),
        correlation_id=correlation_id,
        action=TaskAction.SUMMARIZE,
        adaptation_disposition=AdaptationDisposition.PRESERVE,
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
        reasons=(),
    )

    assert result.correlation_id == correlation_id


def test_action_is_preserved() -> None:
    result = OrchestrationDirective.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.VERIFY,
        adaptation_disposition=AdaptationDisposition.PRESERVE,
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
        reasons=(),
    )

    assert result.action is TaskAction.VERIFY


@pytest.mark.parametrize(
    "adaptation_disposition",
    list(AdaptationDisposition),
)
def test_all_adaptation_dispositions_are_representable(
    adaptation_disposition: AdaptationDisposition,
) -> None:
    result = make_directive(
        adaptation_disposition=adaptation_disposition,
    )

    assert result.adaptation_disposition is adaptation_disposition


@pytest.mark.parametrize(
    "orchestration_disposition",
    list(OrchestrationDisposition),
)
def test_all_orchestration_dispositions_are_representable(
    orchestration_disposition: OrchestrationDisposition,
) -> None:
    result = make_directive(
        orchestration_disposition=orchestration_disposition,
    )

    assert result.orchestration_disposition is orchestration_disposition


def test_reasons_are_preserved() -> None:
    reasons = ("first", "second")

    result = make_directive(
        reasons=reasons,
    )

    assert result.reasons == reasons


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        OrchestrationDirective.create(
            context_id="invalid",
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            adaptation_disposition=AdaptationDisposition.PRESERVE,
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=False,
            review_required=False,
            reasons=(),
        )


def test_correlation_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        OrchestrationDirective.create(
            context_id=uuid4(),
            correlation_id="invalid",
            action=TaskAction.SUMMARIZE,
            adaptation_disposition=AdaptationDisposition.PRESERVE,
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=False,
            review_required=False,
            reasons=(),
        )


def test_action_must_be_task_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        OrchestrationDirective.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action="summarize",
            adaptation_disposition=AdaptationDisposition.PRESERVE,
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=False,
            review_required=False,
            reasons=(),
        )


def test_adaptation_disposition_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("adaptation_disposition must be an " "AdaptationDisposition"),
    ):
        OrchestrationDirective.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            adaptation_disposition="preserve",
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=False,
            review_required=False,
            reasons=(),
        )


def test_orchestration_disposition_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("orchestration_disposition must be an " "OrchestrationDisposition"),
    ):
        OrchestrationDirective.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            adaptation_disposition=AdaptationDisposition.PRESERVE,
            orchestration_disposition="no_change",
            execution_change_allowed=False,
            review_required=False,
            reasons=(),
        )


def test_execution_change_allowed_must_be_bool() -> None:
    with pytest.raises(
        TypeError,
        match=("execution_change_allowed must be a bool"),
    ):
        OrchestrationDirective.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            adaptation_disposition=AdaptationDisposition.PRESERVE,
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=1,
            review_required=False,
            reasons=(),
        )


def test_review_required_must_be_bool() -> None:
    with pytest.raises(
        TypeError,
        match="review_required must be a bool",
    ):
        OrchestrationDirective.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            adaptation_disposition=AdaptationDisposition.PRESERVE,
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=False,
            review_required=1,
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        OrchestrationDirective.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            adaptation_disposition=AdaptationDisposition.PRESERVE,
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=False,
            review_required=False,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        OrchestrationDirective.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            adaptation_disposition=AdaptationDisposition.PRESERVE,
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=False,
            review_required=False,
            reasons=(123,),
        )


def test_contract_is_frozen() -> None:
    result = make_directive()

    with pytest.raises(FrozenInstanceError):
        result.review_required = True


def test_contract_uses_slots() -> None:
    result = make_directive()

    assert not hasattr(result, "__dict__")


def test_equal_inputs_produce_equal_results() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    first = OrchestrationDirective.create(
        context_id=context_id,
        correlation_id=correlation_id,
        action=TaskAction.SUMMARIZE,
        adaptation_disposition=AdaptationDisposition.ADVISORY,
        orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
        execution_change_allowed=False,
        review_required=False,
        reasons=("reason",),
    )

    second = OrchestrationDirective.create(
        context_id=context_id,
        correlation_id=correlation_id,
        action=TaskAction.SUMMARIZE,
        adaptation_disposition=AdaptationDisposition.ADVISORY,
        orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
        execution_change_allowed=False,
        review_required=False,
        reasons=("reason",),
    )

    assert first == second


def test_contract_contains_no_runtime_fields() -> None:
    forbidden = {
        "provider",
        "model",
        "strategy",
        "retry",
        "timeout",
        "runtime",
        "executor",
        "execution_graph",
        "prompt",
        "chunk_size",
        "streaming",
    }

    assert not (forbidden & set(OrchestrationDirective.__dataclass_fields__))


def test_contract_contains_no_execution_methods() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
        "modify_runtime",
    }

    public_names = {
        name for name in dir(OrchestrationDirective) if not name.startswith("_")
    }

    assert not (forbidden & public_names)
