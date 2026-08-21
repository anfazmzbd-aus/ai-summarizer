"""Tests for V10 experience-informed decision boundary."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    DecisionSupportDisposition,
    DecisionSupportPolicyResult,
    DecisionSupportStatus,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    ExperienceInformedDecision,
    ExperienceInformedDecisionBoundary,
    TaskAction,
    TaskDecision,
)


def make_decision(
    *,
    context_id=None,
    correlation_id=None,
    action: TaskAction = TaskAction.SUMMARIZE,
) -> TaskDecision:
    return TaskDecision.create(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        action=action,
        reason="test decision",
        confidence=1.0,
    )


def make_policy_result(
    *,
    context_id,
    correlation_id,
    action: TaskAction = TaskAction.SUMMARIZE,
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
    reasons: tuple[str, ...] = ("policy reason",),
) -> DecisionSupportPolicyResult:
    support_status_map = {
        DecisionSupportDisposition.PRESERVE: (
            DecisionSupportStatus.NEUTRAL,
            EvidenceAssessmentStatus.MIXED,
        ),
        DecisionSupportDisposition.ADVISORY: (
            DecisionSupportStatus.SUPPORTED,
            EvidenceAssessmentStatus.SUPPORTIVE,
        ),
        DecisionSupportDisposition.CAUTION: (
            DecisionSupportStatus.CAUTION,
            EvidenceAssessmentStatus.CAUTIONARY,
        ),
        DecisionSupportDisposition.REVIEW: (
            DecisionSupportStatus.UNSUPPORTED,
            EvidenceAssessmentStatus.ADVERSE,
        ),
    }

    support_status, evidence_status = support_status_map[disposition]

    return DecisionSupportPolicyResult.create(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        support_status=support_status,
        evidence_status=evidence_status,
        evidence_strength=EvidenceStrength.ESTABLISHED,
        disposition=disposition,
        reasons=reasons,
    )


def make_result(
    *,
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
) -> ExperienceInformedDecision:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=decision.action,
        disposition=disposition,
    )

    return ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )


def test_boundary_returns_experience_informed_decision() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
    )

    result = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    assert isinstance(
        result,
        ExperienceInformedDecision,
    )


def test_original_decision_is_preserved() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
    )

    result = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    assert result.decision is decision
    assert result.decision == decision


def test_policy_result_is_preserved() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
    )

    result = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    assert result.policy_result is policy
    assert result.policy_result == policy


def test_context_provenance_is_preserved() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    policy = make_policy_result(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    result = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    assert result.decision.context_id == context_id
    assert result.policy_result.context_id == context_id


def test_correlation_provenance_is_preserved() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    policy = make_policy_result(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    result = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    assert result.decision.correlation_id == correlation_id
    assert result.policy_result.correlation_id == correlation_id


def test_action_is_preserved() -> None:
    decision = make_decision(
        action=TaskAction.VERIFY,
    )

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=TaskAction.VERIFY,
    )

    result = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    assert result.decision.action is TaskAction.VERIFY
    assert result.policy_result.action is TaskAction.VERIFY


@pytest.mark.parametrize(
    "disposition,expected",
    [
        (
            DecisionSupportDisposition.PRESERVE,
            False,
        ),
        (
            DecisionSupportDisposition.ADVISORY,
            True,
        ),
        (
            DecisionSupportDisposition.CAUTION,
            True,
        ),
        (
            DecisionSupportDisposition.REVIEW,
            True,
        ),
    ],
)
def test_historical_influence_matches_policy(
    disposition: DecisionSupportDisposition,
    expected: bool,
) -> None:
    result = make_result(
        disposition=disposition,
    )

    assert result.historical_influence_applied is expected


def test_preserve_reason_is_added() -> None:
    result = make_result(
        disposition=DecisionSupportDisposition.PRESERVE,
    )

    assert (
        "the original decision is preserved without historical influence"
        in result.reasons
    )


def test_advisory_reason_is_added() -> None:
    result = make_result(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    assert "historical experience is applied as advisory context" in result.reasons


def test_caution_reason_is_added() -> None:
    result = make_result(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    assert "historical experience is applied as cautionary context" in result.reasons


def test_review_reason_is_added() -> None:
    result = make_result(
        disposition=DecisionSupportDisposition.REVIEW,
    )

    assert "historical experience is applied as review context" in result.reasons


def test_upstream_policy_reasons_are_preserved() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        reasons=("first", "second"),
    )

    result = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    assert result.reasons[:2] == ("first", "second")


def test_decision_must_be_task_decision() -> None:
    policy = make_policy_result(
        context_id=uuid4(),
        correlation_id=uuid4(),
    )

    with pytest.raises(
        TypeError,
        match="decision must be a TaskDecision",
    ):
        ExperienceInformedDecisionBoundary().compose(
            "invalid",
            policy,
        )


def test_policy_result_must_be_valid() -> None:
    decision = make_decision()

    with pytest.raises(
        TypeError,
        match=("policy_result must be a DecisionSupportPolicyResult"),
    ):
        ExperienceInformedDecisionBoundary().compose(
            decision,
            "invalid",
        )


def test_context_id_mismatch_is_rejected() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=uuid4(),
        correlation_id=decision.correlation_id,
    )

    with pytest.raises(
        ValueError,
        match=("decision and policy_result context_id must match"),
    ):
        ExperienceInformedDecisionBoundary().compose(
            decision,
            policy,
        )


def test_correlation_id_mismatch_is_rejected() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=uuid4(),
    )

    with pytest.raises(
        ValueError,
        match=("decision and policy_result correlation_id must match"),
    ):
        ExperienceInformedDecisionBoundary().compose(
            decision,
            policy,
        )


def test_action_mismatch_is_rejected() -> None:
    decision = make_decision(
        action=TaskAction.SUMMARIZE,
    )

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=TaskAction.VERIFY,
    )

    with pytest.raises(
        ValueError,
        match=("decision and policy_result action must match"),
    ):
        ExperienceInformedDecisionBoundary().compose(
            decision,
            policy,
        )


def test_contract_rejects_invalid_decision_type() -> None:
    policy = make_policy_result(
        context_id=uuid4(),
        correlation_id=uuid4(),
    )

    with pytest.raises(
        TypeError,
        match="decision must be a TaskDecision",
    ):
        ExperienceInformedDecision(
            decision="invalid",
            policy_result=policy,
            historical_influence_applied=True,
            reasons=(),
        )


def test_contract_rejects_invalid_policy_type() -> None:
    decision = make_decision()

    with pytest.raises(
        TypeError,
        match=("policy_result must be a DecisionSupportPolicyResult"),
    ):
        ExperienceInformedDecision(
            decision=decision,
            policy_result="invalid",
            historical_influence_applied=False,
            reasons=(),
        )


def test_contract_rejects_context_mismatch() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=uuid4(),
        correlation_id=decision.correlation_id,
    )

    with pytest.raises(
        ValueError,
        match=("decision and policy_result context_id must match"),
    ):
        ExperienceInformedDecision(
            decision=decision,
            policy_result=policy,
            historical_influence_applied=True,
            reasons=(),
        )


def test_contract_rejects_correlation_mismatch() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=uuid4(),
    )

    with pytest.raises(
        ValueError,
        match=("decision and policy_result correlation_id must match"),
    ):
        ExperienceInformedDecision(
            decision=decision,
            policy_result=policy,
            historical_influence_applied=True,
            reasons=(),
        )


def test_contract_rejects_action_mismatch() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=TaskAction.VERIFY,
    )

    with pytest.raises(
        ValueError,
        match=("decision and policy_result action must match"),
    ):
        ExperienceInformedDecision(
            decision=decision,
            policy_result=policy,
            historical_influence_applied=True,
            reasons=(),
        )


def test_historical_influence_must_be_bool() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
    )

    with pytest.raises(
        TypeError,
        match="historical_influence_applied must be a bool",
    ):
        ExperienceInformedDecision(
            decision=decision,
            policy_result=policy,
            historical_influence_applied=1,
            reasons=(),
        )


def test_historical_influence_must_match_policy() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    with pytest.raises(
        ValueError,
        match=("historical_influence_applied must match policy_result"),
    ):
        ExperienceInformedDecision(
            decision=decision,
            policy_result=policy,
            historical_influence_applied=False,
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
    )

    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        ExperienceInformedDecision(
            decision=decision,
            policy_result=policy,
            historical_influence_applied=True,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
    )

    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        ExperienceInformedDecision(
            decision=decision,
            policy_result=policy,
            historical_influence_applied=True,
            reasons=(123,),
        )


def test_contract_is_frozen() -> None:
    result = make_result()

    with pytest.raises(FrozenInstanceError):
        result.historical_influence_applied = False


def test_boundary_is_deterministic() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        disposition=DecisionSupportDisposition.CAUTION,
    )

    boundary = ExperienceInformedDecisionBoundary()

    first = boundary.compose(decision, policy)
    second = boundary.compose(decision, policy)

    assert first == second


def test_boundary_does_not_modify_decision() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
    )

    before = decision

    ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    assert decision == before


def test_boundary_does_not_modify_policy_result() -> None:
    decision = make_decision()

    policy = make_policy_result(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
    )

    before = policy

    ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    assert policy == before


def test_result_contains_no_replacement_action() -> None:
    forbidden = {
        "replacement_action",
        "recommended_action",
        "new_action",
        "new_decision",
        "strategy",
        "provider",
        "retry",
        "replan",
        "runtime",
        "executor",
    }

    assert not (forbidden & set(ExperienceInformedDecision.__dataclass_fields__))


def test_boundary_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "recommend",
        "decide",
        "select_strategy",
        "switch_provider",
        "replace",
        "modify",
    }

    public_names = {
        name
        for name in dir(ExperienceInformedDecisionBoundary)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_boundary_exposes_only_compose() -> None:
    public_names = {
        name
        for name in dir(ExperienceInformedDecisionBoundary)
        if not name.startswith("_")
    }

    assert public_names == {"compose"}
