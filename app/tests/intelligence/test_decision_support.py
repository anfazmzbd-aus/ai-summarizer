"""Tests for the V10 bounded decision support contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    DecisionSupportAssessment,
    DecisionSupportBuilder,
    DecisionSupportStatus,
    EvidenceAssessment,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    TaskAction,
    TaskDecision,
)


def make_decision(
    *,
    action: TaskAction = TaskAction.SUMMARIZE,
    context_id=None,
    correlation_id=None,
) -> TaskDecision:
    return TaskDecision.create(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        action=action,
        reason="test decision",
        confidence=1.0,
    )


def make_assessment(
    *,
    action: TaskAction = TaskAction.SUMMARIZE,
    status: EvidenceAssessmentStatus = (EvidenceAssessmentStatus.SUPPORTIVE),
    strength: EvidenceStrength = (EvidenceStrength.ESTABLISHED),
    sample_count: int = 3,
    known_count: int = 3,
    unknown_count: int = 0,
    reasons: tuple[str, ...] = ("historical evidence assessment",),
) -> EvidenceAssessment:
    return EvidenceAssessment.create(
        action=action,
        evidence_strength=strength,
        status=status,
        sample_count=sample_count,
        known_count=known_count,
        unknown_count=unknown_count,
        reasons=reasons,
    )


def make_support(
    *,
    evidence_status: EvidenceAssessmentStatus = (EvidenceAssessmentStatus.SUPPORTIVE),
    evidence_strength: EvidenceStrength = (EvidenceStrength.ESTABLISHED),
    sample_count: int = 3,
    known_count: int = 3,
    unknown_count: int = 0,
) -> DecisionSupportAssessment:
    return DecisionSupportAssessment.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        evidence_status=evidence_status,
        evidence_strength=evidence_strength,
        sample_count=sample_count,
        known_count=known_count,
        unknown_count=unknown_count,
        reasons=("test reason",),
    )


def test_support_status_values_are_stable() -> None:
    assert DecisionSupportStatus.SUPPORTED.value == "supported"
    assert DecisionSupportStatus.CAUTION.value == "caution"
    assert DecisionSupportStatus.UNSUPPORTED.value == "unsupported"
    assert DecisionSupportStatus.NEUTRAL.value == "neutral"


def test_supportive_maps_to_supported() -> None:
    result = make_support(
        evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
    )

    assert result.support_status is DecisionSupportStatus.SUPPORTED


def test_cautionary_maps_to_caution() -> None:
    result = make_support(
        evidence_status=EvidenceAssessmentStatus.CAUTIONARY,
    )

    assert result.support_status is DecisionSupportStatus.CAUTION


def test_adverse_maps_to_unsupported() -> None:
    result = make_support(
        evidence_status=EvidenceAssessmentStatus.ADVERSE,
    )

    assert result.support_status is DecisionSupportStatus.UNSUPPORTED


@pytest.mark.parametrize(
    "status",
    [
        EvidenceAssessmentStatus.NO_EVIDENCE,
        EvidenceAssessmentStatus.INSUFFICIENT,
        EvidenceAssessmentStatus.MIXED,
    ],
)
def test_non_directional_evidence_maps_to_neutral(
    status: EvidenceAssessmentStatus,
) -> None:
    if status is EvidenceAssessmentStatus.NO_EVIDENCE:
        strength = EvidenceStrength.NONE
        sample_count = 0
        known_count = 0
    elif status is EvidenceAssessmentStatus.INSUFFICIENT:
        strength = EvidenceStrength.LIMITED
        sample_count = 2
        known_count = 2
    else:
        strength = EvidenceStrength.ESTABLISHED
        sample_count = 4
        known_count = 4

    result = make_support(
        evidence_status=status,
        evidence_strength=strength,
        sample_count=sample_count,
        known_count=known_count,
    )

    assert result.support_status is DecisionSupportStatus.NEUTRAL


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        DecisionSupportAssessment(
            context_id="invalid",
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            sample_count=3,
            known_count=3,
            unknown_count=0,
            reasons=(),
        )


def test_correlation_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        DecisionSupportAssessment(
            context_id=uuid4(),
            correlation_id="invalid",
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            sample_count=3,
            known_count=3,
            unknown_count=0,
            reasons=(),
        )


def test_action_must_be_task_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        DecisionSupportAssessment(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action="summarize",
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            sample_count=3,
            known_count=3,
            unknown_count=0,
            reasons=(),
        )


def test_support_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("support_status must be a " "DecisionSupportStatus"),
    ):
        DecisionSupportAssessment(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status="supported",
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            sample_count=3,
            known_count=3,
            unknown_count=0,
            reasons=(),
        )


def test_evidence_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("evidence_status must be an " "EvidenceAssessmentStatus"),
    ):
        DecisionSupportAssessment(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.NEUTRAL,
            evidence_status="mixed",
            evidence_strength=EvidenceStrength.ESTABLISHED,
            sample_count=4,
            known_count=4,
            unknown_count=0,
            reasons=(),
        )


def test_evidence_strength_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("evidence_strength must be an EvidenceStrength"),
    ):
        DecisionSupportAssessment(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength="established",
            sample_count=3,
            known_count=3,
            unknown_count=0,
            reasons=(),
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "sample_count",
        "known_count",
        "unknown_count",
    ],
)
def test_counts_must_be_integers(
    field_name: str,
) -> None:
    values = {
        "context_id": uuid4(),
        "correlation_id": uuid4(),
        "action": TaskAction.SUMMARIZE,
        "support_status": DecisionSupportStatus.SUPPORTED,
        "evidence_status": EvidenceAssessmentStatus.SUPPORTIVE,
        "evidence_strength": EvidenceStrength.ESTABLISHED,
        "sample_count": 3,
        "known_count": 3,
        "unknown_count": 0,
        "reasons": (),
    }

    values[field_name] = 1.5

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an integer",
    ):
        DecisionSupportAssessment(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "sample_count",
        "known_count",
        "unknown_count",
    ],
)
def test_counts_reject_boolean(
    field_name: str,
) -> None:
    values = {
        "context_id": uuid4(),
        "correlation_id": uuid4(),
        "action": TaskAction.SUMMARIZE,
        "support_status": DecisionSupportStatus.SUPPORTED,
        "evidence_status": EvidenceAssessmentStatus.SUPPORTIVE,
        "evidence_strength": EvidenceStrength.ESTABLISHED,
        "sample_count": 3,
        "known_count": 3,
        "unknown_count": 0,
        "reasons": (),
    }

    values[field_name] = True

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an integer",
    ):
        DecisionSupportAssessment(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "sample_count",
        "known_count",
        "unknown_count",
    ],
)
def test_counts_must_be_non_negative(
    field_name: str,
) -> None:
    values = {
        "context_id": uuid4(),
        "correlation_id": uuid4(),
        "action": TaskAction.SUMMARIZE,
        "support_status": DecisionSupportStatus.SUPPORTED,
        "evidence_status": EvidenceAssessmentStatus.SUPPORTIVE,
        "evidence_strength": EvidenceStrength.ESTABLISHED,
        "sample_count": 3,
        "known_count": 3,
        "unknown_count": 0,
        "reasons": (),
    }

    values[field_name] = -1

    with pytest.raises(
        ValueError,
        match=(f"{field_name} must be greater than or equal to 0"),
    ):
        DecisionSupportAssessment(**values)


def test_known_and_unknown_must_sum_to_sample() -> None:
    with pytest.raises(
        ValueError,
        match=("known_count and unknown_count " "must sum to sample_count"),
    ):
        DecisionSupportAssessment(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            sample_count=5,
            known_count=3,
            unknown_count=1,
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        DecisionSupportAssessment(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            sample_count=3,
            known_count=3,
            unknown_count=0,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        DecisionSupportAssessment(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            sample_count=3,
            known_count=3,
            unknown_count=0,
            reasons=(123,),
        )


def test_support_status_must_match_evidence_status() -> None:
    with pytest.raises(
        ValueError,
        match=("support_status must match evidence_status"),
    ):
        DecisionSupportAssessment(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.UNSUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            sample_count=3,
            known_count=3,
            unknown_count=0,
            reasons=(),
        )


def test_support_assessment_is_frozen() -> None:
    result = make_support()

    with pytest.raises(FrozenInstanceError):
        result.support_status = DecisionSupportStatus.NEUTRAL


def test_builder_returns_support_assessment() -> None:
    decision = make_decision()
    assessment = make_assessment()

    result = DecisionSupportBuilder().build(
        decision,
        assessment,
    )

    assert isinstance(
        result,
        DecisionSupportAssessment,
    )


def test_builder_preserves_decision_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    result = DecisionSupportBuilder().build(
        decision,
        make_assessment(),
    )

    assert result.context_id == context_id
    assert result.correlation_id == correlation_id


def test_builder_preserves_action() -> None:
    decision = make_decision(
        action=TaskAction.VERIFY,
    )

    assessment = make_assessment(
        action=TaskAction.VERIFY,
    )

    result = DecisionSupportBuilder().build(
        decision,
        assessment,
    )

    assert result.action is TaskAction.VERIFY


def test_builder_preserves_evidence_properties() -> None:
    decision = make_decision()

    assessment = make_assessment(
        status=EvidenceAssessmentStatus.CAUTIONARY,
        sample_count=6,
        known_count=5,
        unknown_count=1,
    )

    result = DecisionSupportBuilder().build(
        decision,
        assessment,
    )

    assert result.evidence_status is EvidenceAssessmentStatus.CAUTIONARY
    assert result.evidence_strength is EvidenceStrength.ESTABLISHED
    assert result.sample_count == 6
    assert result.known_count == 5
    assert result.unknown_count == 1


def test_builder_maps_supportive_to_supported() -> None:
    result = DecisionSupportBuilder().build(
        make_decision(),
        make_assessment(
            status=EvidenceAssessmentStatus.SUPPORTIVE,
        ),
    )

    assert result.support_status is DecisionSupportStatus.SUPPORTED


def test_builder_maps_cautionary_to_caution() -> None:
    result = DecisionSupportBuilder().build(
        make_decision(),
        make_assessment(
            status=EvidenceAssessmentStatus.CAUTIONARY,
        ),
    )

    assert result.support_status is DecisionSupportStatus.CAUTION


def test_builder_maps_adverse_to_unsupported() -> None:
    result = DecisionSupportBuilder().build(
        make_decision(),
        make_assessment(
            status=EvidenceAssessmentStatus.ADVERSE,
        ),
    )

    assert result.support_status is DecisionSupportStatus.UNSUPPORTED


def test_builder_maps_mixed_to_neutral() -> None:
    result = DecisionSupportBuilder().build(
        make_decision(),
        make_assessment(
            status=EvidenceAssessmentStatus.MIXED,
        ),
    )

    assert result.support_status is DecisionSupportStatus.NEUTRAL


def test_builder_preserves_assessment_reasons() -> None:
    assessment = make_assessment(
        reasons=("historical reason",),
    )

    result = DecisionSupportBuilder().build(
        make_decision(),
        assessment,
    )

    assert result.reasons[0] == "historical reason"


def test_supported_reason_is_added() -> None:
    result = DecisionSupportBuilder().build(
        make_decision(),
        make_assessment(
            status=EvidenceAssessmentStatus.SUPPORTIVE,
        ),
    )

    assert "historical evidence supports the current action" in result.reasons


def test_caution_reason_is_added() -> None:
    result = DecisionSupportBuilder().build(
        make_decision(),
        make_assessment(
            status=EvidenceAssessmentStatus.CAUTIONARY,
        ),
    )

    assert any("warrants caution" in reason for reason in result.reasons)


def test_unsupported_reason_is_added() -> None:
    result = DecisionSupportBuilder().build(
        make_decision(),
        make_assessment(
            status=EvidenceAssessmentStatus.ADVERSE,
        ),
    )

    assert "historical evidence does not support the current action" in result.reasons


def test_no_evidence_reason_is_added() -> None:
    assessment = make_assessment(
        status=EvidenceAssessmentStatus.NO_EVIDENCE,
        strength=EvidenceStrength.NONE,
        sample_count=0,
        known_count=0,
    )

    result = DecisionSupportBuilder().build(
        make_decision(),
        assessment,
    )

    assert "historical evidence does not inform the current action" in result.reasons


def test_insufficient_reason_is_added() -> None:
    assessment = make_assessment(
        status=EvidenceAssessmentStatus.INSUFFICIENT,
        strength=EvidenceStrength.LIMITED,
        sample_count=2,
        known_count=2,
    )

    result = DecisionSupportBuilder().build(
        make_decision(),
        assessment,
    )

    assert any(
        "insufficient to support or oppose" in reason for reason in result.reasons
    )


def test_mixed_reason_is_added() -> None:
    result = DecisionSupportBuilder().build(
        make_decision(),
        make_assessment(
            status=EvidenceAssessmentStatus.MIXED,
        ),
    )

    assert any(
        "mixed and does not establish directional support" in reason
        for reason in result.reasons
    )


def test_builder_rejects_invalid_decision() -> None:
    with pytest.raises(
        TypeError,
        match="decision must be a TaskDecision",
    ):
        DecisionSupportBuilder().build(
            "invalid",
            make_assessment(),
        )


def test_builder_rejects_invalid_assessment() -> None:
    with pytest.raises(
        TypeError,
        match=("assessment must be an EvidenceAssessment"),
    ):
        DecisionSupportBuilder().build(
            make_decision(),
            "invalid",
        )


def test_action_mismatch_is_rejected() -> None:
    decision = make_decision(
        action=TaskAction.SUMMARIZE,
    )

    assessment = make_assessment(
        action=TaskAction.VERIFY,
    )

    with pytest.raises(
        ValueError,
        match=("decision and assessment action must match"),
    ):
        DecisionSupportBuilder().build(
            decision,
            assessment,
        )


def test_builder_is_deterministic() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assessment = make_assessment(
        status=EvidenceAssessmentStatus.CAUTIONARY,
        sample_count=5,
        known_count=5,
    )

    builder = DecisionSupportBuilder()

    first = builder.build(
        decision,
        assessment,
    )
    second = builder.build(
        decision,
        assessment,
    )

    assert first == second


def test_builder_does_not_modify_inputs() -> None:
    decision = make_decision()
    assessment = make_assessment()

    decision_before = decision
    assessment_before = assessment

    DecisionSupportBuilder().build(
        decision,
        assessment,
    )

    assert decision == decision_before
    assert assessment == assessment_before


def test_support_contains_no_replacement_decision_fields() -> None:
    forbidden = {
        "replacement_action",
        "recommended_action",
        "new_decision",
        "strategy",
        "provider",
        "retry",
        "replan",
        "policy_result",
        "reward",
    }

    assert not (forbidden & set(DecisionSupportAssessment.__dataclass_fields__))


def test_builder_has_no_policy_or_execution_interface() -> None:
    forbidden = {
        "apply",
        "apply_policy",
        "decide",
        "recommend",
        "execute",
        "retry",
        "replan",
        "adapt",
        "switch_provider",
        "select_strategy",
    }

    public_names = {
        name for name in dir(DecisionSupportBuilder) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_builder_exposes_only_build() -> None:
    public_names = {
        name for name in dir(DecisionSupportBuilder) if not name.startswith("_")
    }

    assert public_names == {"build"}
