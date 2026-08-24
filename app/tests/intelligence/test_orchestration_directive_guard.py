"""Tests for V10 M7 orchestration directive guard boundary."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationDisposition,
    DirectiveValidationStatus,
    OrchestrationDirective,
    OrchestrationDirectiveGuard,
    OrchestrationDirectiveValidation,
    OrchestrationDisposition,
    TaskAction,
)


def make_directive(
    *,
    orchestration_disposition: OrchestrationDisposition,
    execution_change_allowed: bool,
    review_required: bool,
) -> OrchestrationDirective:
    adaptation_map = {
        OrchestrationDisposition.NO_CHANGE: (AdaptationDisposition.PRESERVE),
        OrchestrationDisposition.ADVISORY_CONTEXT: (AdaptationDisposition.ADVISORY),
        OrchestrationDisposition.BOUNDED_CONSTRAINT: (AdaptationDisposition.CONSTRAIN),
        OrchestrationDisposition.REVIEW_REQUIRED: (AdaptationDisposition.REVIEW),
    }

    return OrchestrationDirective.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        adaptation_disposition=(adaptation_map[orchestration_disposition]),
        orchestration_disposition=(orchestration_disposition),
        execution_change_allowed=(execution_change_allowed),
        review_required=review_required,
        reasons=("directive reason",),
    )


def test_validation_status_values_are_stable() -> None:
    assert DirectiveValidationStatus.VALID.value == "valid"
    assert DirectiveValidationStatus.REJECTED.value == "rejected"


@pytest.mark.parametrize(
    "disposition,execution_change,review_required",
    [
        (
            OrchestrationDisposition.NO_CHANGE,
            False,
            False,
        ),
        (
            OrchestrationDisposition.ADVISORY_CONTEXT,
            False,
            False,
        ),
        (
            OrchestrationDisposition.BOUNDED_CONSTRAINT,
            True,
            False,
        ),
        (
            OrchestrationDisposition.REVIEW_REQUIRED,
            False,
            True,
        ),
    ],
)
def test_valid_directive_matrix(
    disposition: OrchestrationDisposition,
    execution_change: bool,
    review_required: bool,
) -> None:
    directive = make_directive(
        orchestration_disposition=disposition,
        execution_change_allowed=execution_change,
        review_required=review_required,
    )

    result = OrchestrationDirectiveGuard().validate(directive)

    assert result.status is DirectiveValidationStatus.VALID


def test_no_change_does_not_authorize_execution() -> None:
    result = OrchestrationDirectiveGuard().validate(
        make_directive(
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=False,
            review_required=False,
        )
    )

    assert result.execution_authorized is False
    assert result.review_required is False


def test_advisory_does_not_authorize_execution() -> None:
    result = OrchestrationDirectiveGuard().validate(
        make_directive(
            orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
            execution_change_allowed=False,
            review_required=False,
        )
    )

    assert result.execution_authorized is False
    assert result.review_required is False


def test_bounded_constraint_authorizes_execution() -> None:
    result = OrchestrationDirectiveGuard().validate(
        make_directive(
            orchestration_disposition=(OrchestrationDisposition.BOUNDED_CONSTRAINT),
            execution_change_allowed=True,
            review_required=False,
        )
    )

    assert result.execution_authorized is True
    assert result.review_required is False


def test_review_requires_review_without_execution_authority() -> None:
    result = OrchestrationDirectiveGuard().validate(
        make_directive(
            orchestration_disposition=(OrchestrationDisposition.REVIEW_REQUIRED),
            execution_change_allowed=False,
            review_required=True,
        )
    )

    assert result.execution_authorized is False
    assert result.review_required is True


@pytest.mark.parametrize(
    "disposition,execution_change,review_required",
    [
        (
            OrchestrationDisposition.NO_CHANGE,
            True,
            False,
        ),
        (
            OrchestrationDisposition.NO_CHANGE,
            False,
            True,
        ),
        (
            OrchestrationDisposition.ADVISORY_CONTEXT,
            True,
            False,
        ),
        (
            OrchestrationDisposition.ADVISORY_CONTEXT,
            False,
            True,
        ),
        (
            OrchestrationDisposition.BOUNDED_CONSTRAINT,
            False,
            False,
        ),
        (
            OrchestrationDisposition.BOUNDED_CONSTRAINT,
            True,
            True,
        ),
        (
            OrchestrationDisposition.REVIEW_REQUIRED,
            True,
            True,
        ),
        (
            OrchestrationDisposition.REVIEW_REQUIRED,
            False,
            False,
        ),
    ],
)
def test_invalid_authority_matrix_is_rejected(
    disposition: OrchestrationDisposition,
    execution_change: bool,
    review_required: bool,
) -> None:
    directive = make_directive(
        orchestration_disposition=disposition,
        execution_change_allowed=execution_change,
        review_required=review_required,
    )

    result = OrchestrationDirectiveGuard().validate(directive)

    assert result.status is DirectiveValidationStatus.REJECTED
    assert result.execution_authorized is False
    assert result.review_required is False


def test_rejected_result_contains_guard_reason() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=True,
        review_required=False,
    )

    result = OrchestrationDirectiveGuard().validate(directive)

    assert any(
        "cannot authorize execution changes" in reason for reason in result.reasons
    )


def test_valid_result_preserves_directive_reasons() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
        execution_change_allowed=False,
        review_required=False,
    )

    result = OrchestrationDirectiveGuard().validate(directive)

    assert result.reasons[0] == "directive reason"


def test_valid_result_adds_validation_reason() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
    )

    result = OrchestrationDirectiveGuard().validate(directive)

    assert any(
        "passed bounded authority validation" in reason for reason in result.reasons
    )


def test_guard_rejects_invalid_input() -> None:
    with pytest.raises(
        TypeError,
        match=("directive must be an OrchestrationDirective"),
    ):
        OrchestrationDirectiveGuard().validate("invalid")


def test_validation_requires_directive_type() -> None:
    with pytest.raises(
        TypeError,
        match=("directive must be an OrchestrationDirective"),
    ):
        OrchestrationDirectiveValidation(
            directive="invalid",
            status=DirectiveValidationStatus.VALID,
            execution_authorized=False,
            review_required=False,
            reasons=(),
        )


def test_validation_status_must_be_valid() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
    )

    with pytest.raises(
        TypeError,
        match=("status must be a DirectiveValidationStatus"),
    ):
        OrchestrationDirectiveValidation(
            directive=directive,
            status="valid",
            execution_authorized=False,
            review_required=False,
            reasons=(),
        )


def test_execution_authorized_must_be_bool() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
    )

    with pytest.raises(
        TypeError,
        match=("execution_authorized must be a bool"),
    ):
        OrchestrationDirectiveValidation(
            directive=directive,
            status=DirectiveValidationStatus.VALID,
            execution_authorized=1,
            review_required=False,
            reasons=(),
        )


def test_review_required_must_be_bool() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
    )

    with pytest.raises(
        TypeError,
        match="review_required must be a bool",
    ):
        OrchestrationDirectiveValidation(
            directive=directive,
            status=DirectiveValidationStatus.VALID,
            execution_authorized=False,
            review_required=1,
            reasons=(),
        )


def test_rejected_validation_cannot_authorize_execution() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
    )

    with pytest.raises(
        ValueError,
        match=("rejected validation cannot authorize execution"),
    ):
        OrchestrationDirectiveValidation(
            directive=directive,
            status=DirectiveValidationStatus.REJECTED,
            execution_authorized=True,
            review_required=False,
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
    )

    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        OrchestrationDirectiveValidation(
            directive=directive,
            status=DirectiveValidationStatus.VALID,
            execution_authorized=False,
            review_required=False,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=False,
        review_required=False,
    )

    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        OrchestrationDirectiveValidation(
            directive=directive,
            status=DirectiveValidationStatus.VALID,
            execution_authorized=False,
            review_required=False,
            reasons=(123,),
        )


def test_validation_is_frozen() -> None:
    result = OrchestrationDirectiveGuard().validate(
        make_directive(
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            execution_change_allowed=False,
            review_required=False,
        )
    )

    with pytest.raises(FrozenInstanceError):
        result.execution_authorized = True


def test_guard_is_deterministic() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.BOUNDED_CONSTRAINT),
        execution_change_allowed=True,
        review_required=False,
    )

    guard = OrchestrationDirectiveGuard()

    first = guard.validate(directive)
    second = guard.validate(directive)

    assert first == second


def test_guard_does_not_modify_directive() -> None:
    directive = make_directive(
        orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
        execution_change_allowed=False,
        review_required=False,
    )

    before = directive

    OrchestrationDirectiveGuard().validate(directive)

    assert directive == before


def test_validation_contains_no_runtime_configuration() -> None:
    forbidden = {
        "provider",
        "model",
        "strategy",
        "retry",
        "timeout",
        "executor",
        "execution_graph",
        "prompt",
        "chunk_size",
        "streaming",
    }

    assert not (forbidden & set(OrchestrationDirectiveValidation.__dataclass_fields__))


def test_guard_has_no_runtime_interface() -> None:
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
        name for name in dir(OrchestrationDirectiveGuard) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_guard_exposes_only_validate() -> None:
    public_names = {
        name for name in dir(OrchestrationDirectiveGuard) if not name.startswith("_")
    }

    assert public_names == {"validate"}
