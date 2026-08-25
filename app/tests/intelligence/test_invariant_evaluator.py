"""Tests for V10 M9 intelligence invariant evaluation engine."""

from __future__ import annotations

import pytest

from app.intelligence import (
    ExecutionIntegrationMode,
    IntelligenceInvariant,
    IntelligenceInvariantCategory,
    IntelligenceInvariantEvaluator,
    IntelligenceInvariantSeverity,
    IntelligenceObservabilityIntegrationBoundary,
    IntelligenceObservabilityStatus,
    InvariantEvaluationResult,
)
from app.tests.intelligence.test_observability_integration import (
    make_chain,
)


def make_snapshot(
    mode: ExecutionIntegrationMode = (ExecutionIntegrationMode.ADVISORY),
):
    trace, summary, event = make_chain(
        mode=mode,
    )

    return IntelligenceObservabilityIntegrationBoundary().compose(
        trace,
        summary,
        event,
    )


def get_invariant(
    invariant_id: str,
) -> IntelligenceInvariant:
    for invariant in IntelligenceInvariantEvaluator.canonical_invariants():
        if invariant.invariant_id == invariant_id:
            return invariant

    raise AssertionError(f"missing invariant {invariant_id}")


def test_canonical_invariant_ids_are_stable() -> None:
    ids = tuple(
        invariant.invariant_id
        for invariant in (IntelligenceInvariantEvaluator.canonical_invariants())
    )

    assert ids == (
        "INV-PROV-001",
        "INV-AUTH-001",
        "INV-AUTH-002",
        "INV-AUTH-003",
        "INV-STATE-001",
        "INV-OBS-001",
        "INV-RUNTIME-001",
    )


def test_canonical_invariants_are_deterministic() -> None:
    first = IntelligenceInvariantEvaluator.canonical_invariants()
    second = IntelligenceInvariantEvaluator.canonical_invariants()

    assert first == second


def test_evaluate_returns_result() -> None:
    invariant = get_invariant("INV-PROV-001")

    result = IntelligenceInvariantEvaluator().evaluate(
        invariant,
        make_snapshot(),
    )

    assert isinstance(
        result,
        InvariantEvaluationResult,
    )


def test_valid_snapshot_passes_provenance() -> None:
    result = IntelligenceInvariantEvaluator().evaluate(
        get_invariant("INV-PROV-001"),
        make_snapshot(),
    )

    assert result.passed is True


def test_preserve_does_not_authorize_execution() -> None:
    result = IntelligenceInvariantEvaluator().evaluate(
        get_invariant("INV-AUTH-001"),
        make_snapshot(ExecutionIntegrationMode.PRESERVE),
    )

    assert result.passed is True


def test_advisory_does_not_authorize_execution() -> None:
    result = IntelligenceInvariantEvaluator().evaluate(
        get_invariant("INV-AUTH-002"),
        make_snapshot(ExecutionIntegrationMode.ADVISORY),
    )

    assert result.passed is True


def test_review_does_not_authorize_execution() -> None:
    result = IntelligenceInvariantEvaluator().evaluate(
        get_invariant("INV-AUTH-003"),
        make_snapshot(ExecutionIntegrationMode.REVIEW),
    )

    assert result.passed is True


@pytest.mark.parametrize(
    "mode",
    list(ExecutionIntegrationMode),
)
def test_valid_lifecycle_passes_adaptation_state(
    mode: ExecutionIntegrationMode,
) -> None:
    result = IntelligenceInvariantEvaluator().evaluate(
        get_invariant("INV-STATE-001"),
        make_snapshot(mode),
    )

    assert result.passed is True


@pytest.mark.parametrize(
    "mode",
    list(ExecutionIntegrationMode),
)
def test_valid_lifecycle_passes_observability_authority(
    mode: ExecutionIntegrationMode,
) -> None:
    result = IntelligenceInvariantEvaluator().evaluate(
        get_invariant("INV-OBS-001"),
        make_snapshot(mode),
    )

    assert result.passed is True


@pytest.mark.parametrize(
    "mode",
    list(ExecutionIntegrationMode),
)
def test_valid_lifecycle_passes_runtime_isolation(
    mode: ExecutionIntegrationMode,
) -> None:
    result = IntelligenceInvariantEvaluator().evaluate(
        get_invariant("INV-RUNTIME-001"),
        make_snapshot(mode),
    )

    assert result.passed is True


@pytest.mark.parametrize(
    "mode",
    list(ExecutionIntegrationMode),
)
def test_all_canonical_invariants_pass_valid_lifecycle(
    mode: ExecutionIntegrationMode,
) -> None:
    results = IntelligenceInvariantEvaluator().evaluate_all(make_snapshot(mode))

    assert all(result.passed for result in results)


def test_evaluate_all_returns_all_results() -> None:
    results = IntelligenceInvariantEvaluator().evaluate_all(make_snapshot())

    assert len(results) == 7


def test_evaluate_all_preserves_invariant_order() -> None:
    results = IntelligenceInvariantEvaluator().evaluate_all(make_snapshot())

    assert tuple(result.invariant.invariant_id for result in results) == (
        "INV-PROV-001",
        "INV-AUTH-001",
        "INV-AUTH-002",
        "INV-AUTH-003",
        "INV-STATE-001",
        "INV-OBS-001",
        "INV-RUNTIME-001",
    )


def test_invalid_invariant_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=("invariant must be an " "IntelligenceInvariant"),
    ):
        IntelligenceInvariantEvaluator().evaluate(
            "invalid",
            make_snapshot(),
        )


def test_invalid_snapshot_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=("snapshot must be an " "IntelligenceObservabilitySnapshot"),
    ):
        IntelligenceInvariantEvaluator().evaluate(
            get_invariant("INV-PROV-001"),
            "invalid",
        )


def test_evaluate_all_rejects_invalid_snapshot() -> None:
    with pytest.raises(
        TypeError,
        match=("snapshot must be an " "IntelligenceObservabilitySnapshot"),
    ):
        (IntelligenceInvariantEvaluator().evaluate_all("invalid"))


def test_unknown_invariant_is_rejected() -> None:
    invariant = IntelligenceInvariant.create(
        invariant_id="INV-UNKNOWN-001",
        category=(IntelligenceInvariantCategory.PROVENANCE),
        severity=(IntelligenceInvariantSeverity.REQUIRED),
        description="unknown invariant",
    )

    with pytest.raises(
        ValueError,
        match=("unsupported invariant_id: " "INV-UNKNOWN-001"),
    ):
        IntelligenceInvariantEvaluator().evaluate(
            invariant,
            make_snapshot(),
        )


def test_evaluation_is_deterministic() -> None:
    snapshot = make_snapshot(ExecutionIntegrationMode.CONSTRAINED)

    evaluator = IntelligenceInvariantEvaluator()

    first = evaluator.evaluate_all(snapshot)
    second = evaluator.evaluate_all(snapshot)

    assert first == second


def test_evaluator_does_not_modify_snapshot() -> None:
    snapshot = make_snapshot()

    before = snapshot

    (IntelligenceInvariantEvaluator().evaluate_all(snapshot))

    assert snapshot == before


def test_invariants_do_not_change_observability_status() -> None:
    snapshot = make_snapshot(ExecutionIntegrationMode.ADVISORY)

    before_status = snapshot.status

    (IntelligenceInvariantEvaluator().evaluate_all(snapshot))

    assert snapshot.status is before_status is IntelligenceObservabilityStatus.ADVISORY


def test_evaluator_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "adapt",
        "run",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
        "modify_runtime",
        "emit",
        "publish",
    }

    public_names = {
        name for name in dir(IntelligenceInvariantEvaluator) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_evaluator_public_interface_is_bounded() -> None:
    public_names = {
        name for name in dir(IntelligenceInvariantEvaluator) if not name.startswith("_")
    }

    assert public_names == {
        "canonical_invariants",
        "evaluate",
        "evaluate_all",
    }
