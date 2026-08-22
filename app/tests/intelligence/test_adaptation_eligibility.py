"""Tests for V10 adaptation eligibility contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID, uuid4

import pytest

from app.intelligence import (
    AdaptationEligibility,
    AdaptationEligibilityStatus,
    DecisionSupportDisposition,
    TaskAction,
)


def make_eligibility(
    *,
    context_id: UUID | None = None,
    correlation_id: UUID | None = None,
    action: TaskAction = TaskAction.SUMMARIZE,
    policy_disposition: DecisionSupportDisposition = (
        DecisionSupportDisposition.ADVISORY
    ),
    historical_influence_applied: bool = True,
    status: AdaptationEligibilityStatus = (AdaptationEligibilityStatus.ELIGIBLE),
    reasons: tuple[str, ...] = ("eligible for adaptation",),
) -> AdaptationEligibility:
    return AdaptationEligibility.create(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        action=action,
        policy_disposition=policy_disposition,
        historical_influence_applied=(historical_influence_applied),
        status=status,
        reasons=reasons,
    )


def test_create_returns_adaptation_eligibility() -> None:
    result = make_eligibility()

    assert isinstance(result, AdaptationEligibility)


def test_context_id_is_preserved() -> None:
    context_id = uuid4()

    result = make_eligibility(
        context_id=context_id,
    )

    assert result.context_id == context_id


def test_correlation_id_is_preserved() -> None:
    correlation_id = uuid4()

    result = make_eligibility(
        correlation_id=correlation_id,
    )

    assert result.correlation_id == correlation_id


def test_action_is_preserved() -> None:
    result = make_eligibility(
        action=TaskAction.VERIFY,
    )

    assert result.action is TaskAction.VERIFY


@pytest.mark.parametrize(
    "disposition",
    list(DecisionSupportDisposition),
)
def test_policy_disposition_is_preserved(
    disposition: DecisionSupportDisposition,
) -> None:
    result = make_eligibility(
        policy_disposition=disposition,
    )

    assert result.policy_disposition is disposition


@pytest.mark.parametrize(
    "historical_influence_applied",
    [True, False],
)
def test_historical_influence_is_preserved(
    historical_influence_applied: bool,
) -> None:
    result = make_eligibility(
        historical_influence_applied=(historical_influence_applied),
    )

    assert result.historical_influence_applied is historical_influence_applied


@pytest.mark.parametrize(
    "status",
    list(AdaptationEligibilityStatus),
)
def test_status_is_preserved(
    status: AdaptationEligibilityStatus,
) -> None:
    result = make_eligibility(
        status=status,
    )

    assert result.status is status


def test_reasons_are_preserved() -> None:
    reasons = (
        "first reason",
        "second reason",
    )

    result = make_eligibility(
        reasons=reasons,
    )

    assert result.reasons == reasons


def test_empty_reasons_are_allowed() -> None:
    result = make_eligibility(
        reasons=(),
    )

    assert result.reasons == ()


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        AdaptationEligibility.create(
            context_id="invalid",
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            policy_disposition=(DecisionSupportDisposition.ADVISORY),
            historical_influence_applied=True,
            status=AdaptationEligibilityStatus.ELIGIBLE,
            reasons=(),
        )


def test_correlation_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        AdaptationEligibility.create(
            context_id=uuid4(),
            correlation_id="invalid",
            action=TaskAction.SUMMARIZE,
            policy_disposition=(DecisionSupportDisposition.ADVISORY),
            historical_influence_applied=True,
            status=AdaptationEligibilityStatus.ELIGIBLE,
            reasons=(),
        )


def test_action_must_be_task_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        AdaptationEligibility.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action="summarize",
            policy_disposition=(DecisionSupportDisposition.ADVISORY),
            historical_influence_applied=True,
            status=AdaptationEligibilityStatus.ELIGIBLE,
            reasons=(),
        )


def test_policy_disposition_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("policy_disposition must be a " "DecisionSupportDisposition"),
    ):
        AdaptationEligibility.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            policy_disposition="advisory",
            historical_influence_applied=True,
            status=AdaptationEligibilityStatus.ELIGIBLE,
            reasons=(),
        )


def test_historical_influence_must_be_bool() -> None:
    with pytest.raises(
        TypeError,
        match=("historical_influence_applied must be a bool"),
    ):
        AdaptationEligibility.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            policy_disposition=(DecisionSupportDisposition.ADVISORY),
            historical_influence_applied=1,
            status=AdaptationEligibilityStatus.ELIGIBLE,
            reasons=(),
        )


def test_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("status must be an AdaptationEligibilityStatus"),
    ):
        AdaptationEligibility.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            policy_disposition=(DecisionSupportDisposition.ADVISORY),
            historical_influence_applied=True,
            status="eligible",
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        AdaptationEligibility.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            policy_disposition=(DecisionSupportDisposition.ADVISORY),
            historical_influence_applied=True,
            status=AdaptationEligibilityStatus.ELIGIBLE,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        AdaptationEligibility.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            policy_disposition=(DecisionSupportDisposition.ADVISORY),
            historical_influence_applied=True,
            status=AdaptationEligibilityStatus.ELIGIBLE,
            reasons=(123,),
        )


def test_contract_is_frozen() -> None:
    result = make_eligibility()

    with pytest.raises(FrozenInstanceError):
        result.status = AdaptationEligibilityStatus.INELIGIBLE


def test_contract_uses_slots() -> None:
    result = make_eligibility()

    assert not hasattr(result, "__dict__")


def test_equal_inputs_produce_equal_contracts() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    first = make_eligibility(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    second = make_eligibility(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert first == second


def test_status_values_are_stable() -> None:
    assert AdaptationEligibilityStatus.INELIGIBLE.value == "ineligible"
    assert AdaptationEligibilityStatus.ELIGIBLE.value == "eligible"
    assert AdaptationEligibilityStatus.REVIEW_ONLY.value == "review_only"


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

    assert not (forbidden & set(AdaptationEligibility.__dataclass_fields__))


def test_contract_contains_no_adaptation_instruction() -> None:
    forbidden = {
        "adaptation",
        "adaptation_action",
        "recommended_action",
        "replacement_action",
        "new_action",
        "constraint",
    }

    assert not (forbidden & set(AdaptationEligibility.__dataclass_fields__))
