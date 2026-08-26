"""Tests for V10 M10 compatibility and regression boundary."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    CanonicalV10CompatibilityManifest,
    V10CompatibilityDomain,
    V10CompatibilityEvidence,
    V10CompatibilityEvaluator,
    V10CompatibilityManifest,
    V10CompatibilityRequirement,
    V10CompatibilityResult,
    V10CompatibilityStatus,
)


def make_evidence(
    *,
    domain: V10CompatibilityDomain,
    passed: bool = True,
) -> V10CompatibilityEvidence:
    return V10CompatibilityEvidence(
        domain=domain,
        passed=passed,
        reasons=(
            "regression evidence passed" if passed else "regression evidence failed",
        ),
    )


def make_all_green_evidence():
    return tuple(
        make_evidence(
            domain=domain,
        )
        for domain in V10CompatibilityDomain
    )


def test_domain_values_are_stable() -> None:
    assert V10CompatibilityDomain.V7_EXECUTION.value == "v7_execution"
    assert V10CompatibilityDomain.V8_RUNTIME.value == "v8_runtime"
    assert V10CompatibilityDomain.V9_PROVIDER.value == "v9_provider"
    assert V10CompatibilityDomain.V9_SUMMARIZATION.value == "v9_summarization"
    assert V10CompatibilityDomain.V9_RESILIENCE.value == "v9_resilience"
    assert V10CompatibilityDomain.V9_STREAMING.value == "v9_streaming"
    assert V10CompatibilityDomain.V10_INTELLIGENCE.value == "v10_intelligence"


def test_status_values_are_stable() -> None:
    assert V10CompatibilityStatus.COMPATIBLE.value == "compatible"
    assert V10CompatibilityStatus.INCOMPATIBLE.value == "incompatible"


def test_requirement_creation() -> None:
    result = V10CompatibilityRequirement(
        domain=V10CompatibilityDomain.V7_EXECUTION,
        description="test requirement",
    )

    assert result.required is True


def test_requirement_rejects_invalid_domain() -> None:
    with pytest.raises(
        TypeError,
        match=("domain must be a V10CompatibilityDomain"),
    ):
        V10CompatibilityRequirement(
            domain="v7_execution",
            description="test",
        )


def test_requirement_rejects_empty_description() -> None:
    with pytest.raises(
        ValueError,
        match="description must not be empty",
    ):
        V10CompatibilityRequirement(
            domain=V10CompatibilityDomain.V7_EXECUTION,
            description="",
        )


def test_manifest_requires_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="requirements must be a tuple",
    ):
        V10CompatibilityManifest(
            requirements=[],
        )


def test_manifest_requires_requirements() -> None:
    with pytest.raises(
        ValueError,
        match="requirements must not be empty",
    ):
        V10CompatibilityManifest(
            requirements=(),
        )


def test_manifest_rejects_duplicate_domains() -> None:
    requirement = V10CompatibilityRequirement(
        domain=V10CompatibilityDomain.V7_EXECUTION,
        description="test",
    )

    with pytest.raises(
        ValueError,
        match=("compatibility domains must be unique"),
    ):
        V10CompatibilityManifest(
            requirements=(
                requirement,
                requirement,
            )
        )


def test_canonical_manifest_contains_all_domains() -> None:
    manifest = CanonicalV10CompatibilityManifest.build()

    assert manifest.required_domains == tuple(V10CompatibilityDomain)


def test_canonical_manifest_contains_seven_domains() -> None:
    manifest = CanonicalV10CompatibilityManifest.build()

    assert len(manifest.required_domains) == 7


def test_canonical_manifest_is_deterministic() -> None:
    assert (
        CanonicalV10CompatibilityManifest.build()
        == CanonicalV10CompatibilityManifest.build()
    )


def test_evidence_creation() -> None:
    result = make_evidence(
        domain=V10CompatibilityDomain.V8_RUNTIME,
    )

    assert result.passed is True


def test_evidence_passed_requires_bool() -> None:
    with pytest.raises(
        TypeError,
        match="passed must be a bool",
    ):
        V10CompatibilityEvidence(
            domain=V10CompatibilityDomain.V8_RUNTIME,
            passed=1,
            reasons=(),
        )


def test_evidence_reasons_require_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        V10CompatibilityEvidence(
            domain=V10CompatibilityDomain.V8_RUNTIME,
            passed=True,
            reasons=["passed"],
        )


def test_all_green_evidence_is_compatible() -> None:
    result = V10CompatibilityEvaluator().evaluate(
        CanonicalV10CompatibilityManifest.build(),
        make_all_green_evidence(),
    )

    assert result.status is V10CompatibilityStatus.COMPATIBLE
    assert result.required_domains == 7
    assert result.passed_domains == 7
    assert result.failed_domains == 0
    assert result.missing_domains == ()


@pytest.mark.parametrize(
    "failed_domain",
    list(V10CompatibilityDomain),
)
def test_any_failed_domain_is_incompatible(
    failed_domain: V10CompatibilityDomain,
) -> None:
    evidence = tuple(
        make_evidence(
            domain=domain,
            passed=domain is not failed_domain,
        )
        for domain in V10CompatibilityDomain
    )

    result = V10CompatibilityEvaluator().evaluate(
        CanonicalV10CompatibilityManifest.build(),
        evidence,
    )

    assert result.status is V10CompatibilityStatus.INCOMPATIBLE
    assert result.failed_domains == 1


@pytest.mark.parametrize(
    "missing_domain",
    list(V10CompatibilityDomain),
)
def test_any_missing_required_domain_is_incompatible(
    missing_domain: V10CompatibilityDomain,
) -> None:
    evidence = tuple(
        make_evidence(
            domain=domain,
        )
        for domain in V10CompatibilityDomain
        if domain is not missing_domain
    )

    result = V10CompatibilityEvaluator().evaluate(
        CanonicalV10CompatibilityManifest.build(),
        evidence,
    )

    assert result.status is V10CompatibilityStatus.INCOMPATIBLE
    assert result.missing_domains == (missing_domain,)


def test_duplicate_evidence_domains_are_rejected() -> None:
    item = make_evidence(
        domain=V10CompatibilityDomain.V7_EXECUTION,
    )

    with pytest.raises(
        ValueError,
        match=("compatibility evidence domains must be unique"),
    ):
        V10CompatibilityEvaluator().evaluate(
            CanonicalV10CompatibilityManifest.build(),
            (
                item,
                item,
            ),
        )


def test_invalid_manifest_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=("manifest must be a V10CompatibilityManifest"),
    ):
        V10CompatibilityEvaluator().evaluate(
            "invalid",
            make_all_green_evidence(),
        )


def test_invalid_evidence_collection_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="evidence must be a tuple",
    ):
        V10CompatibilityEvaluator().evaluate(
            CanonicalV10CompatibilityManifest.build(),
            [],
        )


def test_result_is_frozen() -> None:
    result = V10CompatibilityEvaluator().evaluate(
        CanonicalV10CompatibilityManifest.build(),
        make_all_green_evidence(),
    )

    with pytest.raises(FrozenInstanceError):
        result.status = V10CompatibilityStatus.INCOMPATIBLE


def test_evidence_is_frozen() -> None:
    result = make_evidence(
        domain=V10CompatibilityDomain.V9_PROVIDER,
    )

    with pytest.raises(FrozenInstanceError):
        result.passed = False


def test_manifest_uses_slots() -> None:
    assert not hasattr(
        CanonicalV10CompatibilityManifest.build(),
        "__dict__",
    )


def test_result_uses_slots() -> None:
    result = V10CompatibilityEvaluator().evaluate(
        CanonicalV10CompatibilityManifest.build(),
        make_all_green_evidence(),
    )

    assert not hasattr(result, "__dict__")


def test_evaluator_is_deterministic() -> None:
    manifest = CanonicalV10CompatibilityManifest.build()
    evidence = make_all_green_evidence()

    evaluator = V10CompatibilityEvaluator()

    first = evaluator.evaluate(
        manifest,
        evidence,
    )
    second = evaluator.evaluate(
        manifest,
        evidence,
    )

    assert first == second


def test_evaluator_does_not_modify_evidence() -> None:
    manifest = CanonicalV10CompatibilityManifest.build()
    evidence = make_all_green_evidence()

    before = evidence

    V10CompatibilityEvaluator().evaluate(
        manifest,
        evidence,
    )

    assert evidence == before


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

    assert not (forbidden & set(V10CompatibilityResult.__dataclass_fields__))


def test_result_contains_no_scoring() -> None:
    forbidden = {
        "score",
        "percentage",
        "probability",
        "confidence",
        "quality_score",
        "risk_score",
    }

    assert not (forbidden & set(V10CompatibilityResult.__dataclass_fields__))


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
        name for name in dir(V10CompatibilityEvaluator) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_evaluator_exposes_only_evaluate() -> None:
    public_names = {
        name for name in dir(V10CompatibilityEvaluator) if not name.startswith("_")
    }

    assert public_names == {"evaluate"}
