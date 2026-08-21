"""Tests for V10 bounded decision support policy."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    BoundedDecisionSupportPolicy,
    DecisionSupportAssessment,
    DecisionSupportDisposition,
    DecisionSupportPolicyResult,
    DecisionSupportStatus,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    TaskAction,
)


def make_support(
    *,
    support_status: DecisionSupportStatus = (DecisionSupportStatus.SUPPORTED),
    evidence_status: EvidenceAssessmentStatus = (EvidenceAssessmentStatus.SUPPORTIVE),
    evidence_strength: EvidenceStrength = (EvidenceStrength.ESTABLISHED),
    context_id=None,
    correlation_id=None,
    action: TaskAction = TaskAction.SUMMARIZE,
    sample_count: int = 3,
    known_count: int = 3,
    unknown_count: int = 0,
    reasons: tuple[str, ...] = ("historical support assessment",),
) -> DecisionSupportAssessment:
    return DecisionSupportAssessment(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        action=action,
        support_status=support_status,
        evidence_status=evidence_status,
        evidence_strength=evidence_strength,
        sample_count=sample_count,
        known_count=known_count,
        unknown_count=unknown_count,
        reasons=reasons,
    )


def make_result(
    *,
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
) -> DecisionSupportPolicyResult:
    return DecisionSupportPolicyResult.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        support_status=DecisionSupportStatus.SUPPORTED,
        evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
        evidence_strength=EvidenceStrength.ESTABLISHED,
        disposition=disposition,
        reasons=("policy reason",),
    )


def test_disposition_values_are_stable() -> None:
    assert DecisionSupportDisposition.PRESERVE.value == "preserve"
    assert DecisionSupportDisposition.ADVISORY.value == "advisory"
    assert DecisionSupportDisposition.CAUTION.value == "caution"
    assert DecisionSupportDisposition.REVIEW.value == "review"


def test_supported_established_maps_to_advisory() -> None:
    result = BoundedDecisionSupportPolicy().apply(make_support())

    assert result.disposition is DecisionSupportDisposition.ADVISORY


def test_caution_established_maps_to_caution() -> None:
    result = BoundedDecisionSupportPolicy().apply(
        make_support(
            support_status=DecisionSupportStatus.CAUTION,
            evidence_status=EvidenceAssessmentStatus.CAUTIONARY,
        )
    )

    assert result.disposition is DecisionSupportDisposition.CAUTION


def test_unsupported_established_maps_to_review() -> None:
    result = BoundedDecisionSupportPolicy().apply(
        make_support(
            support_status=DecisionSupportStatus.UNSUPPORTED,
            evidence_status=EvidenceAssessmentStatus.ADVERSE,
        )
    )

    assert result.disposition is DecisionSupportDisposition.REVIEW


@pytest.mark.parametrize(
    "status,evidence_status",
    [
        (
            DecisionSupportStatus.NEUTRAL,
            EvidenceAssessmentStatus.NO_EVIDENCE,
        ),
        (
            DecisionSupportStatus.NEUTRAL,
            EvidenceAssessmentStatus.INSUFFICIENT,
        ),
        (
            DecisionSupportStatus.NEUTRAL,
            EvidenceAssessmentStatus.MIXED,
        ),
    ],
)
def test_neutral_support_maps_to_preserve(
    status: DecisionSupportStatus,
    evidence_status: EvidenceAssessmentStatus,
) -> None:
    result = BoundedDecisionSupportPolicy().apply(
        make_support(
            support_status=status,
            evidence_status=evidence_status,
        )
    )

    assert result.disposition is DecisionSupportDisposition.PRESERVE


def test_no_evidence_strength_forces_preserve() -> None:
    result = BoundedDecisionSupportPolicy().apply(
        make_support(
            support_status=DecisionSupportStatus.NEUTRAL,
            evidence_status=EvidenceAssessmentStatus.NO_EVIDENCE,
            evidence_strength=EvidenceStrength.NONE,
            sample_count=0,
            known_count=0,
        )
    )

    assert result.disposition is DecisionSupportDisposition.PRESERVE


def test_limited_strength_forces_preserve() -> None:
    result = BoundedDecisionSupportPolicy().apply(
        make_support(
            support_status=DecisionSupportStatus.NEUTRAL,
            evidence_status=EvidenceAssessmentStatus.INSUFFICIENT,
            evidence_strength=EvidenceStrength.LIMITED,
            sample_count=2,
            known_count=2,
        )
    )

    assert result.disposition is DecisionSupportDisposition.PRESERVE


def test_supported_without_established_strength_is_preserved() -> None:
    support = make_support(
        support_status=DecisionSupportStatus.SUPPORTED,
        evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
        evidence_strength=EvidenceStrength.LIMITED,
        sample_count=2,
        known_count=2,
    )

    result = BoundedDecisionSupportPolicy().apply(support)

    assert result.disposition is DecisionSupportDisposition.PRESERVE


def test_caution_without_established_strength_is_preserved() -> None:
    support = make_support(
        support_status=DecisionSupportStatus.CAUTION,
        evidence_status=EvidenceAssessmentStatus.CAUTIONARY,
        evidence_strength=EvidenceStrength.LIMITED,
        sample_count=2,
        known_count=2,
    )

    result = BoundedDecisionSupportPolicy().apply(support)

    assert result.disposition is DecisionSupportDisposition.PRESERVE


def test_unsupported_without_established_strength_is_preserved() -> None:
    support = make_support(
        support_status=DecisionSupportStatus.UNSUPPORTED,
        evidence_status=EvidenceAssessmentStatus.ADVERSE,
        evidence_strength=EvidenceStrength.LIMITED,
        sample_count=2,
        known_count=2,
    )

    result = BoundedDecisionSupportPolicy().apply(support)

    assert result.disposition is DecisionSupportDisposition.PRESERVE


def test_advisory_allows_historical_influence() -> None:
    result = make_result(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    assert result.historical_influence_allowed is True


def test_caution_allows_historical_influence() -> None:
    result = make_result(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    assert result.historical_influence_allowed is True


def test_review_allows_historical_influence() -> None:
    result = make_result(
        disposition=DecisionSupportDisposition.REVIEW,
    )

    assert result.historical_influence_allowed is True


def test_preserve_disallows_historical_influence() -> None:
    result = make_result(
        disposition=DecisionSupportDisposition.PRESERVE,
    )

    assert result.historical_influence_allowed is False


def test_result_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        DecisionSupportPolicyResult(
            context_id="invalid",
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=True,
            reasons=(),
        )


def test_result_correlation_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id="invalid",
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=True,
            reasons=(),
        )


def test_result_action_must_be_task_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action="summarize",
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=True,
            reasons=(),
        )


def test_result_support_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("support_status must be a DecisionSupportStatus"),
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status="supported",
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=True,
            reasons=(),
        )


def test_result_evidence_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("evidence_status must be an EvidenceAssessmentStatus"),
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status="supportive",
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=True,
            reasons=(),
        )


def test_result_evidence_strength_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("evidence_strength must be an EvidenceStrength"),
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength="established",
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=True,
            reasons=(),
        )


def test_result_disposition_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("disposition must be a DecisionSupportDisposition"),
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition="advisory",
            historical_influence_allowed=True,
            reasons=(),
        )


def test_influence_allowed_must_be_bool() -> None:
    with pytest.raises(
        TypeError,
        match=("historical_influence_allowed must be a bool"),
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=1,
            reasons=(),
        )


def test_influence_flag_must_match_preserve() -> None:
    with pytest.raises(
        ValueError,
        match=("historical_influence_allowed must match disposition"),
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.NEUTRAL,
            evidence_status=EvidenceAssessmentStatus.MIXED,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.PRESERVE,
            historical_influence_allowed=True,
            reasons=(),
        )


def test_influence_flag_must_match_directional_disposition() -> None:
    with pytest.raises(
        ValueError,
        match=("historical_influence_allowed must match disposition"),
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=False,
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=True,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        DecisionSupportPolicyResult(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            support_status=DecisionSupportStatus.SUPPORTED,
            evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            disposition=DecisionSupportDisposition.ADVISORY,
            historical_influence_allowed=True,
            reasons=(123,),
        )


def test_policy_preserves_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    support = make_support(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    result = BoundedDecisionSupportPolicy().apply(support)

    assert result.context_id == context_id
    assert result.correlation_id == correlation_id
    assert result.action is TaskAction.SUMMARIZE


def test_policy_preserves_support_semantics() -> None:
    support = make_support(
        support_status=DecisionSupportStatus.CAUTION,
        evidence_status=EvidenceAssessmentStatus.CAUTIONARY,
    )

    result = BoundedDecisionSupportPolicy().apply(support)

    assert result.support_status is DecisionSupportStatus.CAUTION
    assert result.evidence_status is EvidenceAssessmentStatus.CAUTIONARY
    assert result.evidence_strength is EvidenceStrength.ESTABLISHED


def test_policy_preserves_upstream_reasons() -> None:
    support = make_support(
        reasons=("upstream reason",),
    )

    result = BoundedDecisionSupportPolicy().apply(support)

    assert result.reasons[0] == "upstream reason"


def test_advisory_policy_reason_is_added() -> None:
    result = BoundedDecisionSupportPolicy().apply(make_support())

    assert any("advisory support" in reason for reason in result.reasons)


def test_caution_policy_reason_is_added() -> None:
    result = BoundedDecisionSupportPolicy().apply(
        make_support(
            support_status=DecisionSupportStatus.CAUTION,
            evidence_status=EvidenceAssessmentStatus.CAUTIONARY,
        )
    )

    assert any("cautionary context" in reason for reason in result.reasons)


def test_review_policy_reason_is_added() -> None:
    result = BoundedDecisionSupportPolicy().apply(
        make_support(
            support_status=DecisionSupportStatus.UNSUPPORTED,
            evidence_status=EvidenceAssessmentStatus.ADVERSE,
        )
    )

    assert any("warrants decision review" in reason for reason in result.reasons)


def test_non_established_policy_reason_is_added() -> None:
    result = BoundedDecisionSupportPolicy().apply(
        make_support(
            support_status=DecisionSupportStatus.NEUTRAL,
            evidence_status=EvidenceAssessmentStatus.INSUFFICIENT,
            evidence_strength=EvidenceStrength.LIMITED,
            sample_count=2,
            known_count=2,
        )
    )

    assert any("not established enough" in reason for reason in result.reasons)


def test_mixed_established_reason_is_added() -> None:
    result = BoundedDecisionSupportPolicy().apply(
        make_support(
            support_status=DecisionSupportStatus.NEUTRAL,
            evidence_status=EvidenceAssessmentStatus.MIXED,
        )
    )

    assert any(
        "does not establish a directional policy influence" in reason
        for reason in result.reasons
    )


def test_policy_rejects_invalid_support() -> None:
    with pytest.raises(
        TypeError,
        match=("support must be a DecisionSupportAssessment"),
    ):
        BoundedDecisionSupportPolicy().apply("invalid")


def test_policy_is_deterministic() -> None:
    support = make_support(
        support_status=DecisionSupportStatus.CAUTION,
        evidence_status=EvidenceAssessmentStatus.CAUTIONARY,
    )

    policy = BoundedDecisionSupportPolicy()

    first = policy.apply(support)
    second = policy.apply(support)

    assert first == second


def test_policy_does_not_modify_support() -> None:
    support = make_support()
    before = support

    BoundedDecisionSupportPolicy().apply(support)

    assert support == before


def test_policy_result_is_frozen() -> None:
    result = BoundedDecisionSupportPolicy().apply(make_support())

    with pytest.raises(FrozenInstanceError):
        result.disposition = DecisionSupportDisposition.REVIEW


def test_policy_result_contains_no_replacement_action() -> None:
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

    assert not (forbidden & set(DecisionSupportPolicyResult.__dataclass_fields__))


def test_policy_has_no_runtime_or_decision_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "decide",
        "recommend",
        "select_strategy",
        "switch_provider",
        "modify_decision",
        "replace_decision",
    }

    public_names = {
        name for name in dir(BoundedDecisionSupportPolicy) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_policy_exposes_only_apply() -> None:
    public_names = {
        name for name in dir(BoundedDecisionSupportPolicy) if not name.startswith("_")
    }

    assert public_names == {"apply"}
