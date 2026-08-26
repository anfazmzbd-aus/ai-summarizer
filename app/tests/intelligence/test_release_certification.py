"""Tests for V10 M10 release certification report."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    BoundaryStressCase,
    BoundaryStressCategory,
    BoundaryStressResult,
    CanonicalV10CapabilityManifest,
    CanonicalV10CompatibilityManifest,
    IntelligenceHardeningReport,
    IntelligenceHardeningStatus,
    V10ArchitectureCertification,
    V10ArchitectureCertificationEvaluator,
    V10ArchitectureCertificationStatus,
    V10CompatibilityDomain,
    V10CompatibilityEvidence,
    V10CompatibilityEvaluator,
    V10CompatibilityResult,
    V10CompatibilityStatus,
    V10IntegrationScenario,
    V10IntegrationScenarioKind,
    V10IntegrationScenarioResult,
    V10ReleaseCertificationReport,
    V10ReleaseCertificationReportBuilder,
    V10ReleaseReadinessStatus,
    V10ReleaseValidationEvidence,
)


def make_green_hardening_report() -> IntelligenceHardeningReport:
    """Create structurally valid passing hardening evidence."""

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


def make_failed_hardening_report() -> IntelligenceHardeningReport:
    """Create structurally valid failed hardening evidence."""

    case = BoundaryStressCase(
        case_id="RELEASE-STRESS-001",
        category=BoundaryStressCategory.AUTHORITY,
        description="release certification failure evidence",
    )

    result = BoundaryStressResult(
        case=case,
        passed=False,
        exception_type=None,
        reasons=("invalid state was accepted",),
    )

    return IntelligenceHardeningReport(
        status=IntelligenceHardeningStatus.FAILED,
        invariant_results=(),
        scenario_results=(),
        stress_results=(result,),
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


def make_architecture_certification(
    *,
    certified: bool = True,
) -> V10ArchitectureCertification:
    """Create real architecture-certification evidence."""

    hardening = (
        make_green_hardening_report() if certified else make_failed_hardening_report()
    )

    return V10ArchitectureCertificationEvaluator().evaluate(
        CanonicalV10CapabilityManifest.build(),
        hardening,
    )


def make_integration_scenario(
    *,
    scenario_id: str = "V10-REL-001",
) -> V10IntegrationScenario:
    return V10IntegrationScenario(
        scenario_id=scenario_id,
        name="release certification scenario",
        kind=V10IntegrationScenarioKind.PRESERVE,
        execution_authorized=False,
        review_required=False,
        expected_pass=True,
    )


def make_integration_result(
    *,
    passed: bool = True,
    scenario_id: str = "V10-REL-001",
) -> V10IntegrationScenarioResult:
    return V10IntegrationScenarioResult(
        scenario=make_integration_scenario(
            scenario_id=scenario_id,
        ),
        passed=passed,
        reasons=(
            "integration scenario passed" if passed else "integration scenario failed",
        ),
    )


def make_integration_results(
    *,
    passed: bool = True,
) -> tuple[V10IntegrationScenarioResult, ...]:
    return (
        make_integration_result(
            passed=passed,
            scenario_id="V10-REL-001",
        ),
        make_integration_result(
            passed=True,
            scenario_id="V10-REL-002",
        ),
    )


def make_compatibility_evidence(
    *,
    failed_domain: V10CompatibilityDomain | None = None,
) -> tuple[V10CompatibilityEvidence, ...]:
    return tuple(
        V10CompatibilityEvidence(
            domain=domain,
            passed=domain is not failed_domain,
            reasons=(
                ("compatibility passed",)
                if domain is not failed_domain
                else ("compatibility failed",)
            ),
        )
        for domain in V10CompatibilityDomain
    )


def make_compatibility_result(
    *,
    compatible: bool = True,
) -> V10CompatibilityResult:
    evidence = make_compatibility_evidence(
        failed_domain=(None if compatible else V10CompatibilityDomain.V9_PROVIDER)
    )

    return V10CompatibilityEvaluator().evaluate(
        CanonicalV10CompatibilityManifest.build(),
        evidence,
    )


def make_validation_evidence(
    *,
    intelligence_regression_passed: bool = True,
    non_live_regression_passed: bool = True,
    pre_commit_passed: bool = True,
    diff_check_passed: bool = True,
    documentation_complete: bool = True,
    release_blockers_present: bool = False,
) -> V10ReleaseValidationEvidence:
    return V10ReleaseValidationEvidence(
        intelligence_regression_passed=(intelligence_regression_passed),
        non_live_regression_passed=(non_live_regression_passed),
        pre_commit_passed=pre_commit_passed,
        diff_check_passed=diff_check_passed,
        documentation_complete=documentation_complete,
        release_blockers_present=(release_blockers_present),
    )


def build_report(
    *,
    architecture_certified: bool = True,
    integration_passed: bool = True,
    compatible: bool = True,
    intelligence_regression_passed: bool = True,
    non_live_regression_passed: bool = True,
    pre_commit_passed: bool = True,
    diff_check_passed: bool = True,
    documentation_complete: bool = True,
    release_blockers_present: bool = False,
) -> V10ReleaseCertificationReport:
    return V10ReleaseCertificationReportBuilder().build(
        architecture_certification=(
            make_architecture_certification(
                certified=architecture_certified,
            )
        ),
        integration_results=make_integration_results(
            passed=integration_passed,
        ),
        compatibility_result=make_compatibility_result(
            compatible=compatible,
        ),
        validation_evidence=make_validation_evidence(
            intelligence_regression_passed=(intelligence_regression_passed),
            non_live_regression_passed=(non_live_regression_passed),
            pre_commit_passed=pre_commit_passed,
            diff_check_passed=diff_check_passed,
            documentation_complete=(documentation_complete),
            release_blockers_present=(release_blockers_present),
        ),
    )


def test_readiness_status_values_are_stable() -> None:
    assert V10ReleaseReadinessStatus.READY.value == "ready"
    assert V10ReleaseReadinessStatus.NOT_READY.value == "not_ready"


def test_validation_evidence_creation() -> None:
    result = make_validation_evidence()

    assert result.intelligence_regression_passed is True
    assert result.non_live_regression_passed is True
    assert result.pre_commit_passed is True
    assert result.diff_check_passed is True
    assert result.documentation_complete is True
    assert result.release_blockers_present is False


@pytest.mark.parametrize(
    "field_name",
    [
        "intelligence_regression_passed",
        "non_live_regression_passed",
        "pre_commit_passed",
        "diff_check_passed",
        "documentation_complete",
        "release_blockers_present",
    ],
)
def test_validation_evidence_fields_require_bool(
    field_name: str,
) -> None:
    values = {
        "intelligence_regression_passed": True,
        "non_live_regression_passed": True,
        "pre_commit_passed": True,
        "diff_check_passed": True,
        "documentation_complete": True,
        "release_blockers_present": False,
    }

    values[field_name] = 1

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a bool",
    ):
        V10ReleaseValidationEvidence(**values)


def test_validation_evidence_is_frozen() -> None:
    result = make_validation_evidence()

    with pytest.raises(FrozenInstanceError):
        result.pre_commit_passed = False


def test_validation_evidence_uses_slots() -> None:
    result = make_validation_evidence()

    assert not hasattr(result, "__dict__")


def test_all_green_release_evidence_is_ready() -> None:
    result = build_report()

    assert result.status is V10ReleaseReadinessStatus.READY

    assert result.integration_scenarios_passed is True


def test_ready_report_preserves_architecture_certification() -> None:
    result = build_report()

    assert (
        result.architecture_certification.status
        is V10ArchitectureCertificationStatus.CERTIFIED
    )


def test_ready_report_preserves_compatibility_result() -> None:
    result = build_report()

    assert result.compatibility_result.status is V10CompatibilityStatus.COMPATIBLE


def test_ready_report_preserves_validation_evidence() -> None:
    result = build_report()

    assert result.validation_evidence.intelligence_regression_passed is True
    assert result.validation_evidence.non_live_regression_passed is True


def test_architecture_rejection_produces_not_ready() -> None:
    result = build_report(
        architecture_certified=False,
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY


def test_failed_integration_scenario_produces_not_ready() -> None:
    result = build_report(
        integration_passed=False,
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY

    assert result.integration_scenarios_passed is False


def test_empty_integration_results_produce_not_ready() -> None:
    result = V10ReleaseCertificationReportBuilder().build(
        architecture_certification=(make_architecture_certification()),
        integration_results=(),
        compatibility_result=(make_compatibility_result()),
        validation_evidence=(make_validation_evidence()),
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY
    assert result.integration_scenarios_passed is False


def test_incompatible_result_produces_not_ready() -> None:
    result = build_report(
        compatible=False,
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY


def test_failed_intelligence_regression_produces_not_ready() -> None:
    result = build_report(
        intelligence_regression_passed=False,
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY


def test_failed_non_live_regression_produces_not_ready() -> None:
    result = build_report(
        non_live_regression_passed=False,
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY


def test_failed_pre_commit_produces_not_ready() -> None:
    result = build_report(
        pre_commit_passed=False,
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY


def test_failed_diff_check_produces_not_ready() -> None:
    result = build_report(
        diff_check_passed=False,
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY


def test_incomplete_documentation_produces_not_ready() -> None:
    result = build_report(
        documentation_complete=False,
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY


def test_release_blocker_produces_not_ready() -> None:
    result = build_report(
        release_blockers_present=True,
    )

    assert result.status is V10ReleaseReadinessStatus.NOT_READY


@pytest.mark.parametrize(
    "field_name",
    [
        "intelligence_regression_passed",
        "non_live_regression_passed",
        "pre_commit_passed",
        "diff_check_passed",
        "documentation_complete",
    ],
)
def test_each_validation_failure_independently_blocks_release(
    field_name: str,
) -> None:
    kwargs = {
        "intelligence_regression_passed": True,
        "non_live_regression_passed": True,
        "pre_commit_passed": True,
        "diff_check_passed": True,
        "documentation_complete": True,
        "release_blockers_present": False,
    }

    kwargs[field_name] = False

    result = build_report(**kwargs)

    assert result.status is V10ReleaseReadinessStatus.NOT_READY


def test_ready_report_contains_success_reason() -> None:
    result = build_report()

    assert any(
        "V10 release certification passed" in reason for reason in result.reasons
    )


def test_not_ready_report_contains_failure_reason() -> None:
    result = build_report(
        pre_commit_passed=False,
    )

    assert any(
        "V10 release certification failed" in reason for reason in result.reasons
    )


def test_builder_rejects_invalid_architecture_certification() -> None:
    with pytest.raises(
        TypeError,
        match=("architecture_certification must be a " "V10ArchitectureCertification"),
    ):
        V10ReleaseCertificationReportBuilder().build(
            architecture_certification="invalid",
            integration_results=(make_integration_results()),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
        )


def test_builder_rejects_invalid_integration_collection() -> None:
    with pytest.raises(
        TypeError,
        match=("integration_results must be a tuple"),
    ):
        V10ReleaseCertificationReportBuilder().build(
            architecture_certification=(make_architecture_certification()),
            integration_results=[],
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
        )


def test_builder_rejects_invalid_integration_member() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "integration_results must contain " "V10IntegrationScenarioResult values"
        ),
    ):
        V10ReleaseCertificationReportBuilder().build(
            architecture_certification=(make_architecture_certification()),
            integration_results=("invalid",),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
        )


def test_builder_rejects_invalid_compatibility_result() -> None:
    with pytest.raises(
        TypeError,
        match=("compatibility_result must be a " "V10CompatibilityResult"),
    ):
        V10ReleaseCertificationReportBuilder().build(
            architecture_certification=(make_architecture_certification()),
            integration_results=(make_integration_results()),
            compatibility_result="invalid",
            validation_evidence=(make_validation_evidence()),
        )


def test_builder_rejects_invalid_validation_evidence() -> None:
    with pytest.raises(
        TypeError,
        match=("validation_evidence must be a " "V10ReleaseValidationEvidence"),
    ):
        V10ReleaseCertificationReportBuilder().build(
            architecture_certification=(make_architecture_certification()),
            integration_results=(make_integration_results()),
            compatibility_result=(make_compatibility_result()),
            validation_evidence="invalid",
        )


def test_ready_contract_rejects_failed_architecture() -> None:
    with pytest.raises(
        ValueError,
        match=("READY status requires all release " "requirements to pass"),
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.READY,
            architecture_certification=(
                make_architecture_certification(
                    certified=False,
                )
            ),
            integration_results=(make_integration_results()),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=True,
            reasons=("invalid ready state",),
        )


def test_ready_contract_rejects_failed_integration() -> None:
    with pytest.raises(
        ValueError,
        match=("READY status requires all release " "requirements to pass"),
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.READY,
            architecture_certification=(make_architecture_certification()),
            integration_results=(
                make_integration_results(
                    passed=False,
                )
            ),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=False,
            reasons=("invalid ready state",),
        )


def test_ready_contract_rejects_incompatibility() -> None:
    with pytest.raises(
        ValueError,
        match=("READY status requires all release " "requirements to pass"),
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.READY,
            architecture_certification=(make_architecture_certification()),
            integration_results=(make_integration_results()),
            compatibility_result=(
                make_compatibility_result(
                    compatible=False,
                )
            ),
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=True,
            reasons=("invalid ready state",),
        )


def test_ready_contract_rejects_validation_failure() -> None:
    with pytest.raises(
        ValueError,
        match=("READY status requires all release " "requirements to pass"),
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.READY,
            architecture_certification=(make_architecture_certification()),
            integration_results=(make_integration_results()),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(
                make_validation_evidence(
                    pre_commit_passed=False,
                )
            ),
            integration_scenarios_passed=True,
            reasons=("invalid ready state",),
        )


def test_not_ready_contract_requires_failure() -> None:
    with pytest.raises(
        ValueError,
        match=("NOT_READY status requires at least one " "release requirement to fail"),
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.NOT_READY,
            architecture_certification=(make_architecture_certification()),
            integration_results=(make_integration_results()),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=True,
            reasons=("invalid not-ready state",),
        )


def test_report_requires_valid_architecture_type() -> None:
    with pytest.raises(
        TypeError,
        match=("architecture_certification must be a " "V10ArchitectureCertification"),
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.NOT_READY,
            architecture_certification="invalid",
            integration_results=(),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=False,
            reasons=("invalid",),
        )


def test_report_requires_integration_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="integration_results must be a tuple",
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.NOT_READY,
            architecture_certification=(make_architecture_certification()),
            integration_results=[],
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=False,
            reasons=("invalid",),
        )


def test_report_requires_valid_compatibility_type() -> None:
    with pytest.raises(
        TypeError,
        match=("compatibility_result must be a " "V10CompatibilityResult"),
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.NOT_READY,
            architecture_certification=(make_architecture_certification()),
            integration_results=(),
            compatibility_result="invalid",
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=False,
            reasons=("invalid",),
        )


def test_report_requires_valid_validation_evidence() -> None:
    with pytest.raises(
        TypeError,
        match=("validation_evidence must be a " "V10ReleaseValidationEvidence"),
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.NOT_READY,
            architecture_certification=(make_architecture_certification()),
            integration_results=(),
            compatibility_result=(make_compatibility_result()),
            validation_evidence="invalid",
            integration_scenarios_passed=False,
            reasons=("invalid",),
        )


def test_report_requires_bool_integration_status() -> None:
    with pytest.raises(
        TypeError,
        match=("integration_scenarios_passed must be a bool"),
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.NOT_READY,
            architecture_certification=(make_architecture_certification()),
            integration_results=(),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=1,
            reasons=("invalid",),
        )


def test_report_reasons_require_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.NOT_READY,
            architecture_certification=(
                make_architecture_certification(
                    certified=False,
                )
            ),
            integration_results=(),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=False,
            reasons=["invalid"],
        )


def test_report_reasons_require_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        V10ReleaseCertificationReport(
            status=V10ReleaseReadinessStatus.NOT_READY,
            architecture_certification=(
                make_architecture_certification(
                    certified=False,
                )
            ),
            integration_results=(),
            compatibility_result=(make_compatibility_result()),
            validation_evidence=(make_validation_evidence()),
            integration_scenarios_passed=False,
            reasons=(123,),
        )


def test_report_is_frozen() -> None:
    result = build_report()

    with pytest.raises(FrozenInstanceError):
        result.status = V10ReleaseReadinessStatus.NOT_READY


def test_report_uses_slots() -> None:
    result = build_report()

    assert not hasattr(result, "__dict__")


def test_builder_is_deterministic() -> None:
    architecture = make_architecture_certification()
    integration = make_integration_results()
    compatibility = make_compatibility_result()
    validation = make_validation_evidence()

    builder = V10ReleaseCertificationReportBuilder()

    first = builder.build(
        architecture_certification=architecture,
        integration_results=integration,
        compatibility_result=compatibility,
        validation_evidence=validation,
    )

    second = builder.build(
        architecture_certification=architecture,
        integration_results=integration,
        compatibility_result=compatibility,
        validation_evidence=validation,
    )

    assert first == second


def test_builder_does_not_modify_inputs() -> None:
    architecture = make_architecture_certification()
    integration = make_integration_results()
    compatibility = make_compatibility_result()
    validation = make_validation_evidence()

    before = (
        architecture,
        integration,
        compatibility,
        validation,
    )

    V10ReleaseCertificationReportBuilder().build(
        architecture_certification=architecture,
        integration_results=integration,
        compatibility_result=compatibility,
        validation_evidence=validation,
    )

    assert before == (
        architecture,
        integration,
        compatibility,
        validation,
    )


def test_report_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(V10ReleaseCertificationReport.__dataclass_fields__))


def test_report_contains_no_scoring() -> None:
    forbidden = {
        "score",
        "percentage",
        "probability",
        "confidence",
        "quality_score",
        "risk_score",
        "readiness_score",
    }

    assert not (forbidden & set(V10ReleaseCertificationReport.__dataclass_fields__))


def test_validation_evidence_contains_no_test_execution_api() -> None:
    forbidden = {
        "pytest",
        "run_tests",
        "execute_tests",
        "run_pre_commit",
        "run_git",
    }

    public_names = {
        name for name in dir(V10ReleaseValidationEvidence) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_builder_has_no_runtime_interface() -> None:
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
        "run_tests",
        "commit",
        "tag",
        "push",
    }

    public_names = {
        name
        for name in dir(V10ReleaseCertificationReportBuilder)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_builder_exposes_only_build() -> None:
    public_names = {
        name
        for name in dir(V10ReleaseCertificationReportBuilder)
        if not name.startswith("_")
    }

    assert public_names == {"build"}
