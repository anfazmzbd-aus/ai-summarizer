"""Tests for V10 M10 release integration scenario evaluation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    BoundaryStressCase,
    BoundaryStressCategory,
    BoundaryStressResult,
    CanonicalV10CapabilityManifest,
    CanonicalV10IntegrationScenarios,
    CanonicalLifecycleScenarios,
    IntelligenceHardeningReport,
    IntelligenceHardeningStatus,
    LifecycleScenarioEvaluator,
    V10ArchitectureCertificationEvaluator,
    V10IntegrationScenarioEvaluator,
    V10IntegrationScenarioKind,
    V10IntegrationScenarioResult,
)


def scenarios_by_kind():
    scenarios = CanonicalV10IntegrationScenarios.all()

    return {
        scenario.kind: scenario
        for scenario in scenarios
        if scenario.kind
        in {
            V10IntegrationScenarioKind.ADVISORY,
            V10IntegrationScenarioKind.CONSTRAINED,
            V10IntegrationScenarioKind.REVIEW,
            V10IntegrationScenarioKind.REJECTED,
            V10IntegrationScenarioKind.CERTIFICATION,
        }
    }


def make_green_hardening_report():
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


def test_advisory_lifecycle_matches() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.ADVISORY]

    lifecycle = LifecycleScenarioEvaluator().evaluate(
        CanonicalLifecycleScenarios.all()[1]
    )

    result = V10IntegrationScenarioEvaluator().evaluate_lifecycle(
        scenario,
        lifecycle,
    )

    assert result.passed is True


def test_constrained_lifecycle_matches() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.CONSTRAINED]

    lifecycle = LifecycleScenarioEvaluator().evaluate(
        CanonicalLifecycleScenarios.all()[2]
    )

    result = V10IntegrationScenarioEvaluator().evaluate_lifecycle(
        scenario,
        lifecycle,
    )

    assert result.passed is True


def test_review_lifecycle_matches() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.REVIEW]

    lifecycle = LifecycleScenarioEvaluator().evaluate(
        CanonicalLifecycleScenarios.all()[3]
    )

    result = V10IntegrationScenarioEvaluator().evaluate_lifecycle(
        scenario,
        lifecycle,
    )

    assert result.passed is True


def test_rejected_stress_matches() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.REJECTED]

    stress = BoundaryStressResult(
        case=BoundaryStressCase(
            case_id="V10-REJECT-001",
            category=BoundaryStressCategory.AUTHORITY,
            description="rejected orchestration",
        ),
        passed=True,
        exception_type="ValueError",
        reasons=("boundary rejected invalid state",),
    )

    result = V10IntegrationScenarioEvaluator().evaluate_rejected(
        scenario,
        stress,
    )

    assert result.passed is True


def test_certification_scenario_matches() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.CERTIFICATION]

    certification = V10ArchitectureCertificationEvaluator().evaluate(
        CanonicalV10CapabilityManifest.build(),
        make_green_hardening_report(),
    )

    result = V10IntegrationScenarioEvaluator().evaluate_certification(
        scenario,
        certification,
    )

    assert result.passed is True


def test_lifecycle_rejects_certification_scenario() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.CERTIFICATION]

    lifecycle = LifecycleScenarioEvaluator().evaluate(
        CanonicalLifecycleScenarios.all()[0]
    )

    with pytest.raises(
        ValueError,
        match=("scenario is not a lifecycle integration scenario"),
    ):
        V10IntegrationScenarioEvaluator().evaluate_lifecycle(
            scenario,
            lifecycle,
        )


def test_rejected_requires_rejected_kind() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.ADVISORY]

    stress = BoundaryStressResult(
        case=BoundaryStressCase(
            case_id="TEST",
            category=BoundaryStressCategory.AUTHORITY,
            description="test",
        ),
        passed=True,
        exception_type="ValueError",
        reasons=("test",),
    )

    with pytest.raises(
        ValueError,
        match=("scenario must be a REJECTED integration scenario"),
    ):
        V10IntegrationScenarioEvaluator().evaluate_rejected(
            scenario,
            stress,
        )


def test_certification_requires_certification_kind() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.ADVISORY]

    certification = V10ArchitectureCertificationEvaluator().evaluate(
        CanonicalV10CapabilityManifest.build(),
        make_green_hardening_report(),
    )

    with pytest.raises(
        ValueError,
        match=("scenario must be a CERTIFICATION " "integration scenario"),
    ):
        (
            V10IntegrationScenarioEvaluator().evaluate_certification(
                scenario,
                certification,
            )
        )


def test_result_is_frozen() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.REJECTED]

    result = V10IntegrationScenarioResult(
        scenario=scenario,
        passed=True,
        reasons=("test",),
    )

    with pytest.raises(FrozenInstanceError):
        result.passed = False


def test_result_uses_slots() -> None:
    scenario = scenarios_by_kind()[V10IntegrationScenarioKind.REJECTED]

    result = V10IntegrationScenarioResult(
        scenario=scenario,
        passed=True,
        reasons=("test",),
    )

    assert not hasattr(result, "__dict__")


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
        for name in dir(V10IntegrationScenarioEvaluator)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_evaluator_interface_is_bounded() -> None:
    public_names = {
        name
        for name in dir(V10IntegrationScenarioEvaluator)
        if not name.startswith("_")
    }

    assert public_names == {
        "evaluate_certification",
        "evaluate_lifecycle",
        "evaluate_rejected",
    }
