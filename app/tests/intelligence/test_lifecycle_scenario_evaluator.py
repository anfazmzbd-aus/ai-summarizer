"""Tests for V10 M9 end-to-end lifecycle scenario evaluation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    AdaptationDisposition,
    CanonicalLifecycleScenarios,
    ExecutionIntegrationMode,
    IntelligenceObservabilityStatus,
    LifecycleScenarioEvaluator,
    LifecycleScenarioResult,
    OrchestrationDisposition,
)


def evaluate(
    scenario_id: str,
) -> LifecycleScenarioResult:
    return LifecycleScenarioEvaluator().evaluate(
        CanonicalLifecycleScenarios.get(scenario_id)
    )


def test_evaluator_returns_scenario_result() -> None:
    result = evaluate("SCN-001")

    assert isinstance(
        result,
        LifecycleScenarioResult,
    )


@pytest.mark.parametrize(
    "scenario_id",
    [
        "SCN-001",
        "SCN-002",
        "SCN-003",
        "SCN-004",
        "SCN-005",
        "SCN-006",
    ],
)
def test_all_canonical_scenarios_pass(
    scenario_id: str,
) -> None:
    result = evaluate(scenario_id)

    assert result.passed is True


def test_normal_preserve_end_to_end() -> None:
    result = evaluate("SCN-001")

    assert result.historical_influence_applied is False
    assert result.adaptation_applied is False

    assert result.adaptation_disposition is AdaptationDisposition.PRESERVE
    assert result.orchestration_disposition is OrchestrationDisposition.NO_CHANGE
    assert result.integration_mode is ExecutionIntegrationMode.PRESERVE
    assert result.observability_status is IntelligenceObservabilityStatus.NORMAL

    assert result.execution_authorized is False
    assert result.review_required is False


def test_advisory_end_to_end() -> None:
    result = evaluate("SCN-002")

    assert result.historical_influence_applied is True
    assert result.adaptation_applied is True

    assert result.adaptation_disposition is AdaptationDisposition.ADVISORY
    assert result.orchestration_disposition is OrchestrationDisposition.ADVISORY_CONTEXT
    assert result.integration_mode is ExecutionIntegrationMode.ADVISORY
    assert result.observability_status is IntelligenceObservabilityStatus.ADVISORY

    assert result.execution_authorized is False
    assert result.review_required is False


def test_constrained_end_to_end() -> None:
    result = evaluate("SCN-003")

    assert result.historical_influence_applied is True
    assert result.adaptation_applied is True

    assert result.adaptation_disposition is AdaptationDisposition.CONSTRAIN
    assert (
        result.orchestration_disposition is OrchestrationDisposition.BOUNDED_CONSTRAINT
    )
    assert result.integration_mode is ExecutionIntegrationMode.CONSTRAINED
    assert result.observability_status is IntelligenceObservabilityStatus.CONSTRAINED

    assert result.execution_authorized is True
    assert result.review_required is False


def test_review_end_to_end() -> None:
    result = evaluate("SCN-004")

    assert result.historical_influence_applied is True
    assert result.adaptation_applied is True

    assert result.adaptation_disposition is AdaptationDisposition.REVIEW
    assert result.orchestration_disposition is OrchestrationDisposition.REVIEW_REQUIRED
    assert result.integration_mode is ExecutionIntegrationMode.REVIEW
    assert (
        result.observability_status is IntelligenceObservabilityStatus.REVIEW_REQUIRED
    )

    assert result.execution_authorized is False
    assert result.review_required is True


def test_no_historical_influence_preserves() -> None:
    result = evaluate("SCN-005")

    assert result.historical_influence_applied is False
    assert result.adaptation_applied is False
    assert result.adaptation_disposition is AdaptationDisposition.PRESERVE
    assert result.integration_mode is ExecutionIntegrationMode.PRESERVE
    assert result.execution_authorized is False


def test_insufficient_evidence_preserves() -> None:
    result = evaluate("SCN-006")

    assert result.historical_influence_applied is False
    assert result.adaptation_applied is False
    assert result.adaptation_disposition is AdaptationDisposition.PRESERVE
    assert result.integration_mode is ExecutionIntegrationMode.PRESERVE
    assert result.execution_authorized is False


def test_preserve_scenarios_have_distinct_reasons() -> None:
    no_history = evaluate("SCN-005")
    insufficient = evaluate("SCN-006")

    assert no_history.reasons != insufficient.reasons

    assert any(
        "historical influence is unavailable" in reason for reason in no_history.reasons
    )

    assert any(
        "historical evidence is insufficient" in reason
        for reason in insufficient.reasons
    )


@pytest.mark.parametrize(
    "scenario_id",
    [
        "SCN-001",
        "SCN-002",
        "SCN-003",
        "SCN-004",
        "SCN-005",
        "SCN-006",
    ],
)
def test_all_invariants_pass_for_each_scenario(
    scenario_id: str,
) -> None:
    result = evaluate(scenario_id)

    assert result.invariant_results
    assert all(invariant_result.passed for invariant_result in result.invariant_results)


def test_each_scenario_evaluates_seven_invariants() -> None:
    result = evaluate("SCN-003")

    assert len(result.invariant_results) == 7


def test_result_preserves_scenario() -> None:
    scenario = CanonicalLifecycleScenarios.get("SCN-002")

    result = LifecycleScenarioEvaluator().evaluate(scenario)

    assert result.scenario is scenario


def test_invalid_scenario_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=("scenario must be a LifecycleScenario"),
    ):
        LifecycleScenarioEvaluator().evaluate("invalid")


def test_evaluate_all_returns_all_results() -> None:
    scenarios = CanonicalLifecycleScenarios.all()

    results = LifecycleScenarioEvaluator().evaluate_all(scenarios)

    assert len(results) == 6


def test_evaluate_all_preserves_scenario_order() -> None:
    scenarios = CanonicalLifecycleScenarios.all()

    results = LifecycleScenarioEvaluator().evaluate_all(scenarios)

    assert tuple(result.scenario.scenario_id for result in results) == (
        "SCN-001",
        "SCN-002",
        "SCN-003",
        "SCN-004",
        "SCN-005",
        "SCN-006",
    )


def test_evaluate_all_requires_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="scenarios must be a tuple",
    ):
        LifecycleScenarioEvaluator().evaluate_all(
            list(CanonicalLifecycleScenarios.all())
        )


def test_evaluate_all_rejects_invalid_member() -> None:
    with pytest.raises(
        TypeError,
        match=("scenarios must contain " "LifecycleScenario values"),
    ):
        LifecycleScenarioEvaluator().evaluate_all(
            (
                CanonicalLifecycleScenarios.get("SCN-001"),
                "invalid",
            )
        )


def test_result_is_frozen() -> None:
    result = evaluate("SCN-001")

    with pytest.raises(FrozenInstanceError):
        result.passed = False


def test_result_uses_slots() -> None:
    result = evaluate("SCN-001")

    assert not hasattr(
        result,
        "__dict__",
    )


def test_result_reasons_are_present() -> None:
    result = evaluate("SCN-002")

    assert result.reasons


def test_result_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(LifecycleScenarioResult.__dataclass_fields__))


def test_result_contains_no_scoring() -> None:
    forbidden = {
        "score",
        "risk_score",
        "quality_score",
        "confidence_score",
        "probability",
        "percentage",
    }

    assert not (forbidden & set(LifecycleScenarioResult.__dataclass_fields__))


def test_evaluator_is_repeatably_correct() -> None:
    evaluator = LifecycleScenarioEvaluator()
    scenario = CanonicalLifecycleScenarios.get("SCN-003")

    first = evaluator.evaluate(scenario)
    second = evaluator.evaluate(scenario)

    assert first.scenario == second.scenario
    assert first.passed is second.passed
    assert first.historical_influence_applied is second.historical_influence_applied
    assert first.adaptation_applied is second.adaptation_applied
    assert first.adaptation_disposition is second.adaptation_disposition
    assert first.orchestration_disposition is second.orchestration_disposition
    assert first.integration_mode is second.integration_mode
    assert first.observability_status is second.observability_status
    assert first.execution_authorized is second.execution_authorized
    assert first.review_required is second.review_required
    assert first.invariant_results == second.invariant_results


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
        name for name in dir(LifecycleScenarioEvaluator) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_evaluator_public_interface_is_bounded() -> None:
    public_names = {
        name for name in dir(LifecycleScenarioEvaluator) if not name.startswith("_")
    }

    assert public_names == {
        "evaluate",
        "evaluate_all",
    }
