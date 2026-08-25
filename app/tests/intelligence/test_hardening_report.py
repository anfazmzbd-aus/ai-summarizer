"""Tests for V10 M9 integrated intelligence hardening report."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    BoundaryStressCase,
    BoundaryStressCategory,
    BoundaryStressResult,
    CanonicalLifecycleScenarios,
    ExecutionIntegrationMode,
    IntelligenceHardeningReport,
    IntelligenceHardeningReportBuilder,
    IntelligenceHardeningStatus,
    IntelligenceInvariantEvaluator,
    LifecycleScenarioEvaluator,
)
from app.tests.intelligence.test_observability_integration import (
    make_chain,
)
from app.intelligence import (
    IntelligenceObservabilityIntegrationBoundary,
)


def make_invariant_results():
    trace, summary, event = make_chain(mode=ExecutionIntegrationMode.ADVISORY)

    snapshot = IntelligenceObservabilityIntegrationBoundary().compose(
        trace,
        summary,
        event,
    )

    return IntelligenceInvariantEvaluator().evaluate_all(snapshot)


def make_scenario_results():
    return LifecycleScenarioEvaluator().evaluate_all(CanonicalLifecycleScenarios.all())


def make_stress_results(
    *,
    passed: bool = True,
):
    case = BoundaryStressCase(
        case_id="STRESS-REPORT-001",
        category=BoundaryStressCategory.AUTHORITY,
        description="report stress evidence",
    )

    return (
        BoundaryStressResult(
            case=case,
            passed=passed,
            exception_type=("ValueError" if passed else None),
            reasons=("stress evidence passed" if passed else "stress evidence failed",),
        ),
    )


def build_report(
    *,
    stress_passed: bool = True,
) -> IntelligenceHardeningReport:
    return IntelligenceHardeningReportBuilder().build(
        make_invariant_results(),
        make_scenario_results(),
        make_stress_results(
            passed=stress_passed,
        ),
    )


def test_status_values_are_stable() -> None:
    assert IntelligenceHardeningStatus.PASSED.value == "passed"
    assert IntelligenceHardeningStatus.FAILED.value == "failed"


def test_builder_returns_hardening_report() -> None:
    result = build_report()

    assert isinstance(
        result,
        IntelligenceHardeningReport,
    )


def test_all_green_evidence_produces_passed_status() -> None:
    result = build_report()

    assert result.status is IntelligenceHardeningStatus.PASSED


def test_failed_evidence_produces_failed_status() -> None:
    result = build_report(
        stress_passed=False,
    )

    assert result.status is IntelligenceHardeningStatus.FAILED


def test_invariant_counts_are_correct() -> None:
    result = build_report()

    assert result.evaluated_invariants == 7
    assert result.passed_invariants == 7
    assert result.failed_invariants == 0


def test_scenario_counts_are_correct() -> None:
    result = build_report()

    assert result.evaluated_scenarios == 6
    assert result.passed_scenarios == 6
    assert result.failed_scenarios == 0


def test_stress_counts_are_correct() -> None:
    result = build_report()

    assert result.evaluated_stress_cases == 1
    assert result.passed_stress_cases == 1
    assert result.failed_stress_cases == 0


def test_failed_stress_count_is_correct() -> None:
    result = build_report(
        stress_passed=False,
    )

    assert result.evaluated_stress_cases == 1
    assert result.passed_stress_cases == 0
    assert result.failed_stress_cases == 1


def test_passed_report_contains_success_reasons() -> None:
    result = build_report()

    assert "all intelligence invariants passed" in result.reasons
    assert "all canonical lifecycle scenarios passed" in result.reasons
    assert "all boundary stress cases passed" in result.reasons


def test_failed_report_contains_failure_reason() -> None:
    result = build_report(
        stress_passed=False,
    )

    assert any(
        "boundary stress evaluation(s) failed" in reason for reason in result.reasons
    )


def test_builder_preserves_results() -> None:
    invariant_results = make_invariant_results()
    scenario_results = make_scenario_results()
    stress_results = make_stress_results()

    result = IntelligenceHardeningReportBuilder().build(
        invariant_results,
        scenario_results,
        stress_results,
    )

    assert result.invariant_results is invariant_results
    assert result.scenario_results is scenario_results
    assert result.stress_results is stress_results


def test_builder_rejects_invalid_invariant_results() -> None:
    with pytest.raises(
        TypeError,
        match="invariant_results must be a tuple",
    ):
        IntelligenceHardeningReportBuilder().build(
            [],
            make_scenario_results(),
            make_stress_results(),
        )


def test_builder_rejects_invalid_scenario_results() -> None:
    with pytest.raises(
        TypeError,
        match="scenario_results must be a tuple",
    ):
        IntelligenceHardeningReportBuilder().build(
            make_invariant_results(),
            [],
            make_stress_results(),
        )


def test_builder_rejects_invalid_stress_results() -> None:
    with pytest.raises(
        TypeError,
        match="stress_results must be a tuple",
    ):
        IntelligenceHardeningReportBuilder().build(
            make_invariant_results(),
            make_scenario_results(),
            [],
        )


def test_report_rejects_incorrect_invariant_count() -> None:
    report = build_report()

    with pytest.raises(
        ValueError,
        match=("evaluated_invariants must match " "invariant_results"),
    ):
        IntelligenceHardeningReport(
            status=report.status,
            invariant_results=report.invariant_results,
            scenario_results=report.scenario_results,
            stress_results=report.stress_results,
            evaluated_invariants=999,
            passed_invariants=report.passed_invariants,
            failed_invariants=report.failed_invariants,
            evaluated_scenarios=report.evaluated_scenarios,
            passed_scenarios=report.passed_scenarios,
            failed_scenarios=report.failed_scenarios,
            evaluated_stress_cases=(report.evaluated_stress_cases),
            passed_stress_cases=(report.passed_stress_cases),
            failed_stress_cases=(report.failed_stress_cases),
            reasons=report.reasons,
        )


def test_passed_status_cannot_contain_failures() -> None:
    invariant_results = make_invariant_results()
    scenario_results = make_scenario_results()
    stress_results = make_stress_results(
        passed=False,
    )

    with pytest.raises(
        ValueError,
        match=("PASSED hardening status cannot contain failures"),
    ):
        IntelligenceHardeningReport(
            status=IntelligenceHardeningStatus.PASSED,
            invariant_results=invariant_results,
            scenario_results=scenario_results,
            stress_results=stress_results,
            evaluated_invariants=len(invariant_results),
            passed_invariants=len(invariant_results),
            failed_invariants=0,
            evaluated_scenarios=len(scenario_results),
            passed_scenarios=len(scenario_results),
            failed_scenarios=0,
            evaluated_stress_cases=1,
            passed_stress_cases=0,
            failed_stress_cases=1,
            reasons=("invalid",),
        )


def test_failed_status_requires_failure() -> None:
    invariant_results = make_invariant_results()
    scenario_results = make_scenario_results()
    stress_results = make_stress_results()

    with pytest.raises(
        ValueError,
        match=("FAILED hardening status requires at least one failure"),
    ):
        IntelligenceHardeningReport(
            status=IntelligenceHardeningStatus.FAILED,
            invariant_results=invariant_results,
            scenario_results=scenario_results,
            stress_results=stress_results,
            evaluated_invariants=len(invariant_results),
            passed_invariants=len(invariant_results),
            failed_invariants=0,
            evaluated_scenarios=len(scenario_results),
            passed_scenarios=len(scenario_results),
            failed_scenarios=0,
            evaluated_stress_cases=1,
            passed_stress_cases=1,
            failed_stress_cases=0,
            reasons=("invalid",),
        )


def test_report_is_frozen() -> None:
    result = build_report()

    with pytest.raises(FrozenInstanceError):
        result.status = IntelligenceHardeningStatus.FAILED


def test_report_uses_slots() -> None:
    result = build_report()

    assert not hasattr(result, "__dict__")


def test_builder_is_deterministic() -> None:
    invariant_results = make_invariant_results()
    scenario_results = make_scenario_results()
    stress_results = make_stress_results()

    builder = IntelligenceHardeningReportBuilder()

    first = builder.build(
        invariant_results,
        scenario_results,
        stress_results,
    )

    second = builder.build(
        invariant_results,
        scenario_results,
        stress_results,
    )

    assert first == second


def test_builder_does_not_modify_inputs() -> None:
    invariant_results = make_invariant_results()
    scenario_results = make_scenario_results()
    stress_results = make_stress_results()

    before = (
        invariant_results,
        scenario_results,
        stress_results,
    )

    IntelligenceHardeningReportBuilder().build(
        invariant_results,
        scenario_results,
        stress_results,
    )

    assert before == (
        invariant_results,
        scenario_results,
        stress_results,
    )


def test_report_contains_no_scoring() -> None:
    forbidden = {
        "score",
        "percentage",
        "risk_score",
        "quality_score",
        "confidence_score",
        "probability",
    }

    assert not (forbidden & set(IntelligenceHardeningReport.__dataclass_fields__))


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

    assert not (forbidden & set(IntelligenceHardeningReport.__dataclass_fields__))


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
    }

    public_names = {
        name
        for name in dir(IntelligenceHardeningReportBuilder)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_builder_exposes_only_build() -> None:
    public_names = {
        name
        for name in dir(IntelligenceHardeningReportBuilder)
        if not name.startswith("_")
    }

    assert public_names == {"build"}
