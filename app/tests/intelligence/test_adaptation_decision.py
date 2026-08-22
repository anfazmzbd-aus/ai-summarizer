"""Tests for V10 adaptation decision contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationDecision,
    AdaptationDisposition,
    AdaptationEligibilityStatus,
    TaskAction,
)


def make_decision(
    *,
    eligibility_status: AdaptationEligibilityStatus = (
        AdaptationEligibilityStatus.ELIGIBLE
    ),
    disposition: AdaptationDisposition = (AdaptationDisposition.ADVISORY),
    reasons: tuple[str, ...] = ("adaptation reason",),
) -> AdaptationDecision:
    return AdaptationDecision.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        eligibility_status=eligibility_status,
        disposition=disposition,
        reasons=reasons,
    )


def test_disposition_values_are_stable() -> None:
    assert AdaptationDisposition.PRESERVE.value == "preserve"
    assert AdaptationDisposition.ADVISORY.value == "advisory"
    assert AdaptationDisposition.CONSTRAIN.value == "constrain"
    assert AdaptationDisposition.REVIEW.value == "review"


def test_create_returns_adaptation_decision() -> None:
    result = make_decision()

    assert isinstance(result, AdaptationDecision)


@pytest.mark.parametrize(
    "disposition,expected",
    [
        (
            AdaptationDisposition.PRESERVE,
            False,
        ),
        (
            AdaptationDisposition.ADVISORY,
            True,
        ),
        (
            AdaptationDisposition.CONSTRAIN,
            True,
        ),
        (
            AdaptationDisposition.REVIEW,
            True,
        ),
    ],
)
def test_adaptation_applied_matches_disposition(
    disposition: AdaptationDisposition,
    expected: bool,
) -> None:
    result = make_decision(
        disposition=disposition,
    )

    assert result.adaptation_applied is expected


@pytest.mark.parametrize(
    "status",
    list(AdaptationEligibilityStatus),
)
def test_eligibility_status_is_preserved(
    status: AdaptationEligibilityStatus,
) -> None:
    result = make_decision(
        eligibility_status=status,
    )

    assert result.eligibility_status is status


def test_reasons_are_preserved() -> None:
    reasons = (
        "first",
        "second",
    )

    result = make_decision(
        reasons=reasons,
    )

    assert result.reasons == reasons


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        AdaptationDecision.create(
            context_id="invalid",
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
            disposition=AdaptationDisposition.ADVISORY,
            reasons=(),
        )


def test_correlation_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        AdaptationDecision.create(
            context_id=uuid4(),
            correlation_id="invalid",
            action=TaskAction.SUMMARIZE,
            eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
            disposition=AdaptationDisposition.ADVISORY,
            reasons=(),
        )


def test_action_must_be_task_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        AdaptationDecision.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action="summarize",
            eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
            disposition=AdaptationDisposition.ADVISORY,
            reasons=(),
        )


def test_eligibility_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("eligibility_status must be an " "AdaptationEligibilityStatus"),
    ):
        AdaptationDecision.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            eligibility_status="eligible",
            disposition=AdaptationDisposition.ADVISORY,
            reasons=(),
        )


def test_disposition_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("disposition must be an AdaptationDisposition"),
    ):
        AdaptationDecision.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
            disposition="advisory",
            reasons=(),
        )


def test_adaptation_applied_must_be_bool() -> None:
    with pytest.raises(
        TypeError,
        match="adaptation_applied must be a bool",
    ):
        AdaptationDecision(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
            disposition=AdaptationDisposition.ADVISORY,
            adaptation_applied=1,
            reasons=(),
        )


def test_adaptation_applied_must_match_preserve() -> None:
    with pytest.raises(
        ValueError,
        match=("adaptation_applied must match disposition"),
    ):
        AdaptationDecision(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            eligibility_status=(AdaptationEligibilityStatus.INELIGIBLE),
            disposition=AdaptationDisposition.PRESERVE,
            adaptation_applied=True,
            reasons=(),
        )


def test_adaptation_applied_must_match_directional() -> None:
    with pytest.raises(
        ValueError,
        match=("adaptation_applied must match disposition"),
    ):
        AdaptationDecision(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
            disposition=AdaptationDisposition.ADVISORY,
            adaptation_applied=False,
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        AdaptationDecision.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
            disposition=AdaptationDisposition.ADVISORY,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        AdaptationDecision.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
            disposition=AdaptationDisposition.ADVISORY,
            reasons=(123,),
        )


def test_contract_is_frozen() -> None:
    result = make_decision()

    with pytest.raises(FrozenInstanceError):
        result.disposition = AdaptationDisposition.REVIEW


def test_contract_uses_slots() -> None:
    result = make_decision()

    assert not hasattr(result, "__dict__")


def test_equal_inputs_produce_equal_results() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    first = AdaptationDecision.create(
        context_id=context_id,
        correlation_id=correlation_id,
        action=TaskAction.SUMMARIZE,
        eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
        disposition=AdaptationDisposition.ADVISORY,
        reasons=("reason",),
    )

    second = AdaptationDecision.create(
        context_id=context_id,
        correlation_id=correlation_id,
        action=TaskAction.SUMMARIZE,
        eligibility_status=(AdaptationEligibilityStatus.ELIGIBLE),
        disposition=AdaptationDisposition.ADVISORY,
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

    assert not (forbidden & set(AdaptationDecision.__dataclass_fields__))


def test_contract_contains_no_replacement_decision() -> None:
    forbidden = {
        "replacement_action",
        "recommended_action",
        "new_action",
        "new_decision",
        "replacement_decision",
    }

    assert not (forbidden & set(AdaptationDecision.__dataclass_fields__))
