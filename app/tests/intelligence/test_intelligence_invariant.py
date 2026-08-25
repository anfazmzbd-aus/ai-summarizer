"""Tests for V10 M9 intelligence invariant contracts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    IntelligenceInvariant,
    IntelligenceInvariantCategory,
    IntelligenceInvariantSeverity,
    InvariantEvaluationResult,
)


def make_invariant(
    *,
    invariant_id: str = "INV-PROV-001",
    category: IntelligenceInvariantCategory = (
        IntelligenceInvariantCategory.PROVENANCE
    ),
    severity: IntelligenceInvariantSeverity = (IntelligenceInvariantSeverity.CRITICAL),
    description: str = ("context provenance remains consistent"),
) -> IntelligenceInvariant:
    return IntelligenceInvariant.create(
        invariant_id=invariant_id,
        category=category,
        severity=severity,
        description=description,
    )


def make_result(
    *,
    passed: bool = True,
    reasons: tuple[str, ...] = ("invariant satisfied",),
) -> InvariantEvaluationResult:
    return InvariantEvaluationResult.create(
        invariant=make_invariant(),
        passed=passed,
        reasons=reasons,
    )


def test_category_values_are_stable() -> None:
    assert IntelligenceInvariantCategory.PROVENANCE.value == "provenance"
    assert IntelligenceInvariantCategory.AUTHORITY.value == "authority"
    assert IntelligenceInvariantCategory.STATE_CONSISTENCY.value == "state_consistency"
    assert IntelligenceInvariantCategory.IMMUTABILITY.value == "immutability"
    assert IntelligenceInvariantCategory.DETERMINISM.value == "determinism"
    assert IntelligenceInvariantCategory.RUNTIME_ISOLATION.value == "runtime_isolation"


def test_severity_values_are_stable() -> None:
    assert IntelligenceInvariantSeverity.REQUIRED.value == "required"
    assert IntelligenceInvariantSeverity.CRITICAL.value == "critical"


def test_create_returns_invariant() -> None:
    result = make_invariant()

    assert isinstance(
        result,
        IntelligenceInvariant,
    )


@pytest.mark.parametrize(
    "category",
    list(IntelligenceInvariantCategory),
)
def test_all_categories_are_representable(
    category: IntelligenceInvariantCategory,
) -> None:
    result = make_invariant(
        category=category,
    )

    assert result.category is category


@pytest.mark.parametrize(
    "severity",
    list(IntelligenceInvariantSeverity),
)
def test_all_severities_are_representable(
    severity: IntelligenceInvariantSeverity,
) -> None:
    result = make_invariant(
        severity=severity,
    )

    assert result.severity is severity


def test_invariant_id_is_preserved() -> None:
    result = make_invariant(
        invariant_id="INV-AUTH-001",
    )

    assert result.invariant_id == "INV-AUTH-001"


def test_description_is_preserved() -> None:
    result = make_invariant(
        description="test architecture invariant",
    )

    assert result.description == "test architecture invariant"


def test_invariant_id_must_be_string() -> None:
    with pytest.raises(
        TypeError,
        match="invariant_id must be a string",
    ):
        IntelligenceInvariant.create(
            invariant_id=123,
            category=(IntelligenceInvariantCategory.PROVENANCE),
            severity=(IntelligenceInvariantSeverity.CRITICAL),
            description="test",
        )


def test_invariant_id_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="invariant_id must not be empty",
    ):
        IntelligenceInvariant.create(
            invariant_id="",
            category=(IntelligenceInvariantCategory.PROVENANCE),
            severity=(IntelligenceInvariantSeverity.CRITICAL),
            description="test",
        )


def test_category_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("category must be an " "IntelligenceInvariantCategory"),
    ):
        IntelligenceInvariant.create(
            invariant_id="INV-TEST-001",
            category="provenance",
            severity=(IntelligenceInvariantSeverity.CRITICAL),
            description="test",
        )


def test_severity_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("severity must be an " "IntelligenceInvariantSeverity"),
    ):
        IntelligenceInvariant.create(
            invariant_id="INV-TEST-001",
            category=(IntelligenceInvariantCategory.PROVENANCE),
            severity="critical",
            description="test",
        )


def test_description_must_be_string() -> None:
    with pytest.raises(
        TypeError,
        match="description must be a string",
    ):
        IntelligenceInvariant.create(
            invariant_id="INV-TEST-001",
            category=(IntelligenceInvariantCategory.PROVENANCE),
            severity=(IntelligenceInvariantSeverity.CRITICAL),
            description=123,
        )


def test_description_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="description must not be empty",
    ):
        IntelligenceInvariant.create(
            invariant_id="INV-TEST-001",
            category=(IntelligenceInvariantCategory.PROVENANCE),
            severity=(IntelligenceInvariantSeverity.CRITICAL),
            description="",
        )


def test_invariant_is_frozen() -> None:
    result = make_invariant()

    with pytest.raises(FrozenInstanceError):
        result.description = "changed"


def test_invariant_uses_slots() -> None:
    result = make_invariant()

    assert not hasattr(result, "__dict__")


def test_equal_invariants_are_equal() -> None:
    first = make_invariant()
    second = make_invariant()

    assert first == second


def test_result_returns_evaluation_result() -> None:
    result = make_result()

    assert isinstance(
        result,
        InvariantEvaluationResult,
    )


def test_result_preserves_invariant() -> None:
    invariant = make_invariant()

    result = InvariantEvaluationResult.create(
        invariant=invariant,
        passed=True,
        reasons=("passed",),
    )

    assert result.invariant is invariant


@pytest.mark.parametrize(
    "passed",
    [True, False],
)
def test_result_preserves_passed_state(
    passed: bool,
) -> None:
    result = make_result(
        passed=passed,
    )

    assert result.passed is passed


def test_result_preserves_reasons() -> None:
    result = make_result(
        reasons=("first", "second"),
    )

    assert result.reasons == (
        "first",
        "second",
    )


def test_empty_reasons_are_allowed() -> None:
    result = make_result(
        reasons=(),
    )

    assert result.reasons == ()


def test_result_requires_invariant() -> None:
    with pytest.raises(
        TypeError,
        match=("invariant must be an IntelligenceInvariant"),
    ):
        InvariantEvaluationResult.create(
            invariant="invalid",
            passed=True,
            reasons=(),
        )


def test_passed_must_be_bool() -> None:
    with pytest.raises(
        TypeError,
        match="passed must be a bool",
    ):
        InvariantEvaluationResult.create(
            invariant=make_invariant(),
            passed=1,
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        InvariantEvaluationResult.create(
            invariant=make_invariant(),
            passed=True,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        InvariantEvaluationResult.create(
            invariant=make_invariant(),
            passed=True,
            reasons=(123,),
        )


def test_result_is_frozen() -> None:
    result = make_result()

    with pytest.raises(FrozenInstanceError):
        result.passed = False


def test_result_uses_slots() -> None:
    result = make_result()

    assert not hasattr(result, "__dict__")


def test_equal_results_are_equal() -> None:
    first = make_result()
    second = make_result()

    assert first == second


def test_invariant_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(IntelligenceInvariant.__dataclass_fields__))


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
        "streaming",
    }

    assert not (forbidden & set(InvariantEvaluationResult.__dataclass_fields__))


def test_contracts_contain_no_scoring() -> None:
    forbidden = {
        "score",
        "risk_score",
        "quality_score",
        "confidence_score",
        "probability",
        "percentage",
    }

    assert not (forbidden & set(IntelligenceInvariant.__dataclass_fields__))

    assert not (forbidden & set(InvariantEvaluationResult.__dataclass_fields__))


def test_invariant_contains_no_execution_methods() -> None:
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
        name for name in dir(IntelligenceInvariant) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_result_contains_no_execution_methods() -> None:
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
        name for name in dir(InvariantEvaluationResult) if not name.startswith("_")
    }

    assert not (forbidden & public_names)
