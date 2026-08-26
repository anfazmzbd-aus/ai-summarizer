"""Tests for V10 M10 release integration scenario contracts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    CanonicalV10IntegrationScenarios,
    V10IntegrationScenario,
    V10IntegrationScenarioKind,
)


def make_scenario(
    *,
    kind=V10IntegrationScenarioKind.PRESERVE,
    execution_authorized=False,
    review_required=False,
):
    return V10IntegrationScenario(
        scenario_id="V10-TEST-001",
        name="test scenario",
        kind=kind,
        execution_authorized=execution_authorized,
        review_required=review_required,
        expected_pass=True,
    )


def test_kind_values_are_stable() -> None:
    assert V10IntegrationScenarioKind.PRESERVE.value == "preserve"
    assert V10IntegrationScenarioKind.ADVISORY.value == "advisory"
    assert V10IntegrationScenarioKind.CONSTRAINED.value == "constrained"
    assert V10IntegrationScenarioKind.REVIEW.value == "review"
    assert V10IntegrationScenarioKind.REJECTED.value == "rejected"
    assert V10IntegrationScenarioKind.CERTIFICATION.value == "certification"


def test_scenario_creation() -> None:
    result = make_scenario()

    assert result.scenario_id == "V10-TEST-001"
    assert result.expected_pass is True


def test_empty_scenario_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="scenario_id must not be empty",
    ):
        V10IntegrationScenario(
            scenario_id="",
            name="test",
            kind=V10IntegrationScenarioKind.PRESERVE,
            execution_authorized=False,
            review_required=False,
            expected_pass=True,
        )


def test_non_constrained_cannot_authorize_execution() -> None:
    with pytest.raises(
        ValueError,
        match=("only CONSTRAINED scenarios may authorize execution"),
    ):
        make_scenario(
            kind=V10IntegrationScenarioKind.ADVISORY,
            execution_authorized=True,
        )


def test_constrained_requires_execution_authority() -> None:
    with pytest.raises(
        ValueError,
        match=("CONSTRAINED scenarios require execution authority"),
    ):
        make_scenario(
            kind=V10IntegrationScenarioKind.CONSTRAINED,
        )


def test_review_requires_review() -> None:
    with pytest.raises(
        ValueError,
        match="REVIEW scenarios require review",
    ):
        make_scenario(
            kind=V10IntegrationScenarioKind.REVIEW,
        )


def test_only_review_can_require_review() -> None:
    with pytest.raises(
        ValueError,
        match="only REVIEW scenarios may require review",
    ):
        make_scenario(
            review_required=True,
        )


def test_scenario_is_frozen() -> None:
    result = make_scenario()

    with pytest.raises(FrozenInstanceError):
        result.expected_pass = False


def test_scenario_uses_slots() -> None:
    assert not hasattr(make_scenario(), "__dict__")


def test_canonical_matrix_contains_eight_scenarios() -> None:
    assert len(CanonicalV10IntegrationScenarios.all()) == 8


def test_canonical_ids_are_stable() -> None:
    scenarios = CanonicalV10IntegrationScenarios.all()

    assert tuple(scenario.scenario_id for scenario in scenarios) == (
        "V10-INT-001",
        "V10-INT-002",
        "V10-INT-003",
        "V10-INT-004",
        "V10-INT-005",
        "V10-INT-006",
        "V10-INT-007",
        "V10-INT-008",
    )


def test_canonical_ids_are_unique() -> None:
    scenarios = CanonicalV10IntegrationScenarios.all()

    ids = tuple(scenario.scenario_id for scenario in scenarios)

    assert len(ids) == len(set(ids))


def test_only_constrained_authorizes_execution() -> None:
    scenarios = CanonicalV10IntegrationScenarios.all()

    authorized = tuple(
        scenario for scenario in scenarios if scenario.execution_authorized
    )

    assert len(authorized) == 1
    assert authorized[0].kind is V10IntegrationScenarioKind.CONSTRAINED


def test_only_review_requires_review() -> None:
    scenarios = CanonicalV10IntegrationScenarios.all()

    review = tuple(scenario for scenario in scenarios if scenario.review_required)

    assert len(review) == 1
    assert review[0].kind is V10IntegrationScenarioKind.REVIEW


def test_all_canonical_scenarios_expect_pass() -> None:
    assert all(
        scenario.expected_pass for scenario in CanonicalV10IntegrationScenarios.all()
    )


def test_canonical_matrix_is_deterministic() -> None:
    assert (
        CanonicalV10IntegrationScenarios.all() == CanonicalV10IntegrationScenarios.all()
    )
