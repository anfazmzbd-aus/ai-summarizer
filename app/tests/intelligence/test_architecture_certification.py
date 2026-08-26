"""Tests for V10 M10 architecture-wide certification."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    CanonicalV10CapabilityManifest,
    IntelligenceHardeningReport,
    IntelligenceHardeningStatus,
    V10ArchitectureCertification,
    V10ArchitectureCertificationEvaluator,
    V10ArchitectureCertificationStatus,
    V10ArchitectureStatus,
    V10CapabilityManifest,
)


def make_hardening_report() -> IntelligenceHardeningReport:
    return IntelligenceHardeningReport(
        status=IntelligenceHardeningStatus.PASSED,
        invariant_results=(),
        scenario_results=(),
        stress_results=(),
        evaluated_invariants=0,
        passed_invariants=0,
        failed_invariants=0,
        evaluated_scenarios=0,
        passed_scenarios=0,
        failed_scenarios=0,
        evaluated_stress_cases=0,
        passed_stress_cases=0,
        failed_stress_cases=0,
        reasons=("hardening passed",),
    )


def make_certification(
    *,
    status=V10ArchitectureCertificationStatus.CERTIFIED,
    manifest_complete=True,
    feature_frozen=True,
    required_milestones_present=True,
    hardening_passed=True,
) -> V10ArchitectureCertification:
    return V10ArchitectureCertification(
        status=status,
        version="10.0.0",
        manifest_complete=manifest_complete,
        feature_frozen=feature_frozen,
        required_milestones_present=(required_milestones_present),
        hardening_passed=hardening_passed,
        reasons=("test certification",),
    )


def test_status_values_are_stable() -> None:
    assert V10ArchitectureCertificationStatus.CERTIFIED.value == "certified"
    assert V10ArchitectureCertificationStatus.REJECTED.value == "rejected"


def test_certification_creation() -> None:
    result = make_certification()

    assert result.status is V10ArchitectureCertificationStatus.CERTIFIED
    assert result.version == "10.0.0"
    assert result.manifest_complete is True
    assert result.feature_frozen is True
    assert result.required_milestones_present is True
    assert result.hardening_passed is True


def test_certification_requires_valid_status() -> None:
    with pytest.raises(
        TypeError,
        match=("status must be a " "V10ArchitectureCertificationStatus"),
    ):
        V10ArchitectureCertification(
            status="certified",
            version="10.0.0",
            manifest_complete=True,
            feature_frozen=True,
            required_milestones_present=True,
            hardening_passed=True,
            reasons=("test",),
        )


def test_certification_requires_v10_version() -> None:
    with pytest.raises(
        ValueError,
        match="version must be 10.0.0",
    ):
        V10ArchitectureCertification(
            status=(V10ArchitectureCertificationStatus.CERTIFIED),
            version="11.0.0",
            manifest_complete=True,
            feature_frozen=True,
            required_milestones_present=True,
            hardening_passed=True,
            reasons=("test",),
        )


def test_certified_requires_complete_manifest() -> None:
    with pytest.raises(
        ValueError,
        match=("CERTIFIED status requires all " "architecture requirements to pass"),
    ):
        make_certification(
            manifest_complete=False,
        )


def test_certified_requires_feature_freeze() -> None:
    with pytest.raises(
        ValueError,
        match=("CERTIFIED status requires all " "architecture requirements to pass"),
    ):
        make_certification(
            feature_frozen=False,
        )


def test_certified_requires_all_milestones() -> None:
    with pytest.raises(
        ValueError,
        match=("CERTIFIED status requires all " "architecture requirements to pass"),
    ):
        make_certification(
            required_milestones_present=False,
        )


def test_certified_requires_hardening_pass() -> None:
    with pytest.raises(
        ValueError,
        match=("CERTIFIED status requires all " "architecture requirements to pass"),
    ):
        make_certification(
            hardening_passed=False,
        )


def test_rejected_requires_failure() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "REJECTED status requires at least one " "architecture requirement to fail"
        ),
    ):
        make_certification(
            status=(V10ArchitectureCertificationStatus.REJECTED),
        )


def test_canonical_manifest_and_green_hardening_certify() -> None:
    result = V10ArchitectureCertificationEvaluator().evaluate(
        CanonicalV10CapabilityManifest.build(),
        make_hardening_report(),
    )

    assert result.status is V10ArchitectureCertificationStatus.CERTIFIED
    assert result.manifest_complete is True
    assert result.feature_frozen is True
    assert result.required_milestones_present is True
    assert result.hardening_passed is True


def test_incomplete_manifest_is_rejected() -> None:
    canonical = CanonicalV10CapabilityManifest.build()

    manifest = V10CapabilityManifest(
        version=canonical.version,
        architecture_status=(V10ArchitectureStatus.INCOMPLETE),
        feature_frozen=True,
        milestones=canonical.milestones,
    )

    result = V10ArchitectureCertificationEvaluator().evaluate(
        manifest,
        make_hardening_report(),
    )

    assert result.status is V10ArchitectureCertificationStatus.REJECTED
    assert result.manifest_complete is False


def test_non_frozen_manifest_is_rejected() -> None:
    canonical = CanonicalV10CapabilityManifest.build()

    manifest = V10CapabilityManifest(
        version=canonical.version,
        architecture_status=canonical.architecture_status,
        feature_frozen=False,
        milestones=canonical.milestones,
    )

    result = V10ArchitectureCertificationEvaluator().evaluate(
        manifest,
        make_hardening_report(),
    )

    assert result.status is V10ArchitectureCertificationStatus.REJECTED
    assert result.feature_frozen is False


def test_missing_milestone_is_rejected() -> None:
    canonical = CanonicalV10CapabilityManifest.build()

    manifest = V10CapabilityManifest(
        version=canonical.version,
        architecture_status=canonical.architecture_status,
        feature_frozen=True,
        milestones=canonical.milestones[:-1],
    )

    result = V10ArchitectureCertificationEvaluator().evaluate(
        manifest,
        make_hardening_report(),
    )

    assert result.status is V10ArchitectureCertificationStatus.REJECTED
    assert result.required_milestones_present is False


def test_out_of_order_milestones_are_rejected() -> None:
    canonical = CanonicalV10CapabilityManifest.build()

    milestones = (
        canonical.milestones[1],
        canonical.milestones[0],
        *canonical.milestones[2:],
    )

    manifest = V10CapabilityManifest(
        version=canonical.version,
        architecture_status=canonical.architecture_status,
        feature_frozen=True,
        milestones=milestones,
    )

    result = V10ArchitectureCertificationEvaluator().evaluate(
        manifest,
        make_hardening_report(),
    )

    assert result.status is V10ArchitectureCertificationStatus.REJECTED
    assert result.required_milestones_present is False


def test_failed_hardening_is_rejected() -> None:
    # Use a valid FAILED hardening report with one explicit
    # failed stress result rather than inconsistent counters.
    from app.intelligence import (
        BoundaryStressCase,
        BoundaryStressCategory,
        BoundaryStressResult,
    )

    case = BoundaryStressCase(
        case_id="CERT-STRESS-001",
        category=BoundaryStressCategory.AUTHORITY,
        description="certification failure evidence",
    )

    failed_result = BoundaryStressResult(
        case=case,
        passed=False,
        exception_type=None,
        reasons=("invalid state was accepted",),
    )

    report = IntelligenceHardeningReport(
        status=IntelligenceHardeningStatus.FAILED,
        invariant_results=(),
        scenario_results=(),
        stress_results=(failed_result,),
        evaluated_invariants=0,
        passed_invariants=0,
        failed_invariants=0,
        evaluated_scenarios=0,
        passed_scenarios=0,
        failed_scenarios=0,
        evaluated_stress_cases=1,
        passed_stress_cases=0,
        failed_stress_cases=1,
        reasons=("hardening failed",),
    )

    result = V10ArchitectureCertificationEvaluator().evaluate(
        CanonicalV10CapabilityManifest.build(),
        report,
    )

    assert result.status is V10ArchitectureCertificationStatus.REJECTED
    assert result.hardening_passed is False


def test_evaluator_rejects_invalid_manifest_type() -> None:
    with pytest.raises(
        TypeError,
        match="manifest must be a V10CapabilityManifest",
    ):
        V10ArchitectureCertificationEvaluator().evaluate(
            "invalid",
            make_hardening_report(),
        )


def test_evaluator_rejects_invalid_hardening_type() -> None:
    with pytest.raises(
        TypeError,
        match=("hardening_report must be an " "IntelligenceHardeningReport"),
    ):
        V10ArchitectureCertificationEvaluator().evaluate(
            CanonicalV10CapabilityManifest.build(),
            "invalid",
        )


def test_certification_is_frozen() -> None:
    result = make_certification()

    with pytest.raises(FrozenInstanceError):
        result.feature_frozen = False


def test_certification_uses_slots() -> None:
    assert not hasattr(
        make_certification(),
        "__dict__",
    )


def test_evaluator_is_deterministic() -> None:
    manifest = CanonicalV10CapabilityManifest.build()
    report = make_hardening_report()

    evaluator = V10ArchitectureCertificationEvaluator()

    first = evaluator.evaluate(
        manifest,
        report,
    )
    second = evaluator.evaluate(
        manifest,
        report,
    )

    assert first == second


def test_certified_result_contains_success_reason() -> None:
    result = V10ArchitectureCertificationEvaluator().evaluate(
        CanonicalV10CapabilityManifest.build(),
        make_hardening_report(),
    )

    assert "V10 architecture certification passed" in result.reasons


def test_rejected_result_contains_rejection_reason() -> None:
    canonical = CanonicalV10CapabilityManifest.build()

    manifest = V10CapabilityManifest(
        version=canonical.version,
        architecture_status=(V10ArchitectureStatus.INCOMPLETE),
        feature_frozen=True,
        milestones=canonical.milestones,
    )

    result = V10ArchitectureCertificationEvaluator().evaluate(
        manifest,
        make_hardening_report(),
    )

    assert "V10 architecture certification rejected" in result.reasons


def test_certification_contains_no_scoring() -> None:
    forbidden = {
        "score",
        "percentage",
        "confidence",
        "probability",
        "risk_score",
        "quality_score",
    }

    assert not (forbidden & set(V10ArchitectureCertification.__dataclass_fields__))


def test_certification_contains_no_runtime_configuration() -> None:
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
        "streaming",
    }

    assert not (forbidden & set(V10ArchitectureCertification.__dataclass_fields__))


def test_evaluator_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "run",
        "retry",
        "replan",
        "adapt",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
        "modify_runtime",
        "emit",
        "publish",
    }

    public_names = {
        name
        for name in dir(V10ArchitectureCertificationEvaluator)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_evaluator_exposes_only_expected_interface() -> None:
    public_names = {
        name
        for name in dir(V10ArchitectureCertificationEvaluator)
        if not name.startswith("_")
    }

    assert public_names == {
        "REQUIRED_MILESTONES",
        "evaluate",
    }
