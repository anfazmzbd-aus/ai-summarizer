"""Tests for V10 M9 lifecycle scenario contracts and canonical matrix."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    AdaptationDisposition,
    CanonicalLifecycleScenarios,
    ExecutionIntegrationMode,
    IntelligenceObservabilityStatus,
    LifecycleScenario,
    LifecycleScenarioKind,
    OrchestrationDisposition,
)


def make_scenario() -> LifecycleScenario:
    return LifecycleScenario(
        scenario_id="SCN-TEST-001",
        kind=LifecycleScenarioKind.ADVISORY,
        name="test advisory lifecycle",
        historical_influence_expected=True,
        adaptation_expected=True,
        expected_adaptation_disposition=(AdaptationDisposition.ADVISORY),
        expected_orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
        expected_integration_mode=(ExecutionIntegrationMode.ADVISORY),
        expected_observability_status=(IntelligenceObservabilityStatus.ADVISORY),
        execution_authorized_expected=False,
        review_required_expected=False,
    )


def test_kind_values_are_stable() -> None:
    assert LifecycleScenarioKind.NORMAL_PRESERVE.value == "normal_preserve"
    assert LifecycleScenarioKind.ADVISORY.value == "advisory"
    assert LifecycleScenarioKind.CONSTRAINED.value == "constrained"
    assert LifecycleScenarioKind.REVIEW.value == "review"
    assert (
        LifecycleScenarioKind.NO_HISTORICAL_INFLUENCE.value == "no_historical_influence"
    )
    assert LifecycleScenarioKind.INSUFFICIENT_EVIDENCE.value == "insufficient_evidence"


def test_create_returns_lifecycle_scenario() -> None:
    result = make_scenario()

    assert isinstance(result, LifecycleScenario)


def test_scenario_id_is_preserved() -> None:
    result = make_scenario()

    assert result.scenario_id == "SCN-TEST-001"


def test_name_is_preserved() -> None:
    result = make_scenario()

    assert result.name == "test advisory lifecycle"


def test_scenario_id_must_be_string() -> None:
    scenario = make_scenario()

    values = {
        field_name: getattr(scenario, field_name)
        for field_name in scenario.__dataclass_fields__
    }

    values["scenario_id"] = 123

    with pytest.raises(
        TypeError,
        match="scenario_id must be a string",
    ):
        LifecycleScenario(**values)


def test_scenario_id_must_not_be_empty() -> None:
    scenario = make_scenario()

    values = {
        field_name: getattr(scenario, field_name)
        for field_name in scenario.__dataclass_fields__
    }

    values["scenario_id"] = ""

    with pytest.raises(
        ValueError,
        match="scenario_id must not be empty",
    ):
        LifecycleScenario(**values)


def test_kind_must_be_valid() -> None:
    scenario = make_scenario()

    values = {
        field_name: getattr(scenario, field_name)
        for field_name in scenario.__dataclass_fields__
    }

    values["kind"] = "advisory"

    with pytest.raises(
        TypeError,
        match="kind must be a LifecycleScenarioKind",
    ):
        LifecycleScenario(**values)


def test_name_must_be_string() -> None:
    scenario = make_scenario()

    values = {
        field_name: getattr(scenario, field_name)
        for field_name in scenario.__dataclass_fields__
    }

    values["name"] = 123

    with pytest.raises(
        TypeError,
        match="name must be a string",
    ):
        LifecycleScenario(**values)


def test_name_must_not_be_empty() -> None:
    scenario = make_scenario()

    values = {
        field_name: getattr(scenario, field_name)
        for field_name in scenario.__dataclass_fields__
    }

    values["name"] = ""

    with pytest.raises(
        ValueError,
        match="name must not be empty",
    ):
        LifecycleScenario(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "historical_influence_expected",
        "adaptation_expected",
        "execution_authorized_expected",
        "review_required_expected",
    ],
)
def test_boolean_fields_require_bool(
    field_name: str,
) -> None:
    scenario = make_scenario()

    values = {name: getattr(scenario, name) for name in scenario.__dataclass_fields__}

    values[field_name] = 1

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a bool",
    ):
        LifecycleScenario(**values)


def test_adaptation_disposition_must_be_valid() -> None:
    scenario = make_scenario()

    values = {name: getattr(scenario, name) for name in scenario.__dataclass_fields__}

    values["expected_adaptation_disposition"] = "advisory"

    with pytest.raises(
        TypeError,
        match=("expected_adaptation_disposition must be an " "AdaptationDisposition"),
    ):
        LifecycleScenario(**values)


def test_orchestration_disposition_must_be_valid() -> None:
    scenario = make_scenario()

    values = {name: getattr(scenario, name) for name in scenario.__dataclass_fields__}

    values["expected_orchestration_disposition"] = "advisory_context"

    with pytest.raises(
        TypeError,
        match=(
            "expected_orchestration_disposition must be an " "OrchestrationDisposition"
        ),
    ):
        LifecycleScenario(**values)


def test_integration_mode_must_be_valid() -> None:
    scenario = make_scenario()

    values = {name: getattr(scenario, name) for name in scenario.__dataclass_fields__}

    values["expected_integration_mode"] = "advisory"

    with pytest.raises(
        TypeError,
        match=("expected_integration_mode must be an " "ExecutionIntegrationMode"),
    ):
        LifecycleScenario(**values)


def test_observability_status_must_be_valid() -> None:
    scenario = make_scenario()

    values = {name: getattr(scenario, name) for name in scenario.__dataclass_fields__}

    values["expected_observability_status"] = "advisory"

    with pytest.raises(
        TypeError,
        match=(
            "expected_observability_status must be an "
            "IntelligenceObservabilityStatus"
        ),
    ):
        LifecycleScenario(**values)


def test_scenario_is_frozen() -> None:
    scenario = make_scenario()

    with pytest.raises(FrozenInstanceError):
        scenario.name = "changed"


def test_scenario_uses_slots() -> None:
    scenario = make_scenario()

    assert not hasattr(scenario, "__dict__")


def test_equal_scenarios_are_equal() -> None:
    assert make_scenario() == make_scenario()


def test_canonical_scenario_ids_are_stable() -> None:
    scenarios = CanonicalLifecycleScenarios.all()

    assert tuple(scenario.scenario_id for scenario in scenarios) == (
        "SCN-001",
        "SCN-002",
        "SCN-003",
        "SCN-004",
        "SCN-005",
        "SCN-006",
    )


def test_canonical_scenario_kinds_are_stable() -> None:
    scenarios = CanonicalLifecycleScenarios.all()

    assert tuple(scenario.kind for scenario in scenarios) == (
        LifecycleScenarioKind.NORMAL_PRESERVE,
        LifecycleScenarioKind.ADVISORY,
        LifecycleScenarioKind.CONSTRAINED,
        LifecycleScenarioKind.REVIEW,
        LifecycleScenarioKind.NO_HISTORICAL_INFLUENCE,
        LifecycleScenarioKind.INSUFFICIENT_EVIDENCE,
    )


def test_registry_is_deterministic() -> None:
    assert CanonicalLifecycleScenarios.all() == CanonicalLifecycleScenarios.all()


def test_registry_contains_six_scenarios() -> None:
    assert len(CanonicalLifecycleScenarios.all()) == 6


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
def test_get_returns_canonical_scenario(
    scenario_id: str,
) -> None:
    result = CanonicalLifecycleScenarios.get(scenario_id)

    assert result.scenario_id == scenario_id


def test_get_rejects_invalid_id_type() -> None:
    with pytest.raises(
        TypeError,
        match="scenario_id must be a string",
    ):
        CanonicalLifecycleScenarios.get(123)


def test_get_rejects_unknown_scenario() -> None:
    with pytest.raises(
        ValueError,
        match="unknown lifecycle scenario: SCN-999",
    ):
        CanonicalLifecycleScenarios.get("SCN-999")


def test_normal_preserve_matrix() -> None:
    scenario = CanonicalLifecycleScenarios.get("SCN-001")

    assert scenario.historical_influence_expected is False
    assert scenario.adaptation_expected is False
    assert scenario.expected_adaptation_disposition is AdaptationDisposition.PRESERVE
    assert (
        scenario.expected_orchestration_disposition
        is OrchestrationDisposition.NO_CHANGE
    )
    assert scenario.expected_integration_mode is ExecutionIntegrationMode.PRESERVE
    assert (
        scenario.expected_observability_status is IntelligenceObservabilityStatus.NORMAL
    )
    assert scenario.execution_authorized_expected is False
    assert scenario.review_required_expected is False


def test_advisory_matrix() -> None:
    scenario = CanonicalLifecycleScenarios.get("SCN-002")

    assert scenario.historical_influence_expected is True
    assert scenario.adaptation_expected is True
    assert scenario.expected_adaptation_disposition is AdaptationDisposition.ADVISORY
    assert (
        scenario.expected_orchestration_disposition
        is OrchestrationDisposition.ADVISORY_CONTEXT
    )
    assert scenario.expected_integration_mode is ExecutionIntegrationMode.ADVISORY
    assert (
        scenario.expected_observability_status
        is IntelligenceObservabilityStatus.ADVISORY
    )
    assert scenario.execution_authorized_expected is False
    assert scenario.review_required_expected is False


def test_constrained_matrix() -> None:
    scenario = CanonicalLifecycleScenarios.get("SCN-003")

    assert scenario.historical_influence_expected is True
    assert scenario.adaptation_expected is True
    assert scenario.expected_adaptation_disposition is AdaptationDisposition.CONSTRAIN
    assert (
        scenario.expected_orchestration_disposition
        is OrchestrationDisposition.BOUNDED_CONSTRAINT
    )
    assert scenario.expected_integration_mode is ExecutionIntegrationMode.CONSTRAINED
    assert (
        scenario.expected_observability_status
        is IntelligenceObservabilityStatus.CONSTRAINED
    )
    assert scenario.execution_authorized_expected is True
    assert scenario.review_required_expected is False


def test_review_matrix() -> None:
    scenario = CanonicalLifecycleScenarios.get("SCN-004")

    assert scenario.historical_influence_expected is True
    assert scenario.adaptation_expected is True
    assert scenario.expected_adaptation_disposition is AdaptationDisposition.REVIEW
    assert (
        scenario.expected_orchestration_disposition
        is OrchestrationDisposition.REVIEW_REQUIRED
    )
    assert scenario.expected_integration_mode is ExecutionIntegrationMode.REVIEW
    assert (
        scenario.expected_observability_status
        is IntelligenceObservabilityStatus.REVIEW_REQUIRED
    )
    assert scenario.execution_authorized_expected is False
    assert scenario.review_required_expected is True


@pytest.mark.parametrize(
    "scenario_id",
    [
        "SCN-005",
        "SCN-006",
    ],
)
def test_preserve_by_default_scenarios(
    scenario_id: str,
) -> None:
    scenario = CanonicalLifecycleScenarios.get(scenario_id)

    assert scenario.historical_influence_expected is False
    assert scenario.adaptation_expected is False
    assert scenario.expected_adaptation_disposition is AdaptationDisposition.PRESERVE
    assert (
        scenario.expected_orchestration_disposition
        is OrchestrationDisposition.NO_CHANGE
    )
    assert scenario.expected_integration_mode is ExecutionIntegrationMode.PRESERVE
    assert (
        scenario.expected_observability_status is IntelligenceObservabilityStatus.NORMAL
    )
    assert scenario.execution_authorized_expected is False
    assert scenario.review_required_expected is False


def test_scenario_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(LifecycleScenario.__dataclass_fields__))


def test_scenario_contains_no_scoring() -> None:
    forbidden = {
        "score",
        "risk_score",
        "quality_score",
        "confidence_score",
        "probability",
        "percentage",
    }

    assert not (forbidden & set(LifecycleScenario.__dataclass_fields__))


def test_registry_has_no_execution_interface() -> None:
    forbidden = {
        "execute",
        "evaluate",
        "retry",
        "replan",
        "adapt",
        "run",
        "apply_runtime",
    }

    public_names = {
        name for name in dir(CanonicalLifecycleScenarios) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_registry_exposes_only_all_and_get() -> None:
    public_names = {
        name for name in dir(CanonicalLifecycleScenarios) if not name.startswith("_")
    }

    assert public_names == {
        "all",
        "get",
    }
