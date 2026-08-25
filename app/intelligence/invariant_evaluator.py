"""
V10 M9 intelligence invariant evaluation engine.

Evaluates canonical architecture-hardening invariants against existing
read-only V10 intelligence state.

M9.2 performs inspection only. It does not modify architecture state,
repair invalid objects, invoke runtime behavior, or create new authority.
"""

from __future__ import annotations

from dataclasses import fields

from .adaptation_decision import AdaptationDisposition
from .intelligence_invariant import (
    IntelligenceInvariant,
    IntelligenceInvariantCategory,
    IntelligenceInvariantSeverity,
    InvariantEvaluationResult,
)
from .observability_integration import (
    IntelligenceObservabilitySnapshot,
)


class IntelligenceInvariantEvaluator:
    """Evaluate canonical V10 intelligence architecture invariants."""

    def evaluate(
        self,
        invariant: IntelligenceInvariant,
        snapshot: IntelligenceObservabilitySnapshot,
    ) -> InvariantEvaluationResult:
        """Evaluate one invariant against one observability snapshot."""

        if not isinstance(
            invariant,
            IntelligenceInvariant,
        ):
            raise TypeError("invariant must be an IntelligenceInvariant")

        if not isinstance(
            snapshot,
            IntelligenceObservabilitySnapshot,
        ):
            raise TypeError("snapshot must be an " "IntelligenceObservabilitySnapshot")

        evaluator = self._resolve_evaluator(invariant.invariant_id)

        passed, reasons = evaluator(snapshot)

        return InvariantEvaluationResult.create(
            invariant=invariant,
            passed=passed,
            reasons=reasons,
        )

    @staticmethod
    def canonical_invariants() -> tuple[IntelligenceInvariant, ...]:
        """Return the stable initial V10 hardening invariant set."""

        return (
            IntelligenceInvariant.create(
                invariant_id="INV-PROV-001",
                category=(IntelligenceInvariantCategory.PROVENANCE),
                severity=(IntelligenceInvariantSeverity.CRITICAL),
                description=(
                    "observability provenance remains consistent "
                    "across the complete lifecycle"
                ),
            ),
            IntelligenceInvariant.create(
                invariant_id="INV-AUTH-001",
                category=(IntelligenceInvariantCategory.AUTHORITY),
                severity=(IntelligenceInvariantSeverity.CRITICAL),
                description=("PRESERVE adaptation cannot authorize execution"),
            ),
            IntelligenceInvariant.create(
                invariant_id="INV-AUTH-002",
                category=(IntelligenceInvariantCategory.AUTHORITY),
                severity=(IntelligenceInvariantSeverity.CRITICAL),
                description=("ADVISORY adaptation cannot authorize execution"),
            ),
            IntelligenceInvariant.create(
                invariant_id="INV-AUTH-003",
                category=(IntelligenceInvariantCategory.AUTHORITY),
                severity=(IntelligenceInvariantSeverity.CRITICAL),
                description=("REVIEW adaptation cannot authorize execution"),
            ),
            IntelligenceInvariant.create(
                invariant_id="INV-STATE-001",
                category=(IntelligenceInvariantCategory.STATE_CONSISTENCY),
                severity=(IntelligenceInvariantSeverity.CRITICAL),
                description=(
                    "adaptation cannot be applied without " "historical influence"
                ),
            ),
            IntelligenceInvariant.create(
                invariant_id="INV-OBS-001",
                category=(IntelligenceInvariantCategory.AUTHORITY),
                severity=(IntelligenceInvariantSeverity.CRITICAL),
                description=(
                    "observability cannot create execution authority "
                    "beyond integration state"
                ),
            ),
            IntelligenceInvariant.create(
                invariant_id="INV-RUNTIME-001",
                category=(IntelligenceInvariantCategory.RUNTIME_ISOLATION),
                severity=(IntelligenceInvariantSeverity.REQUIRED),
                description=(
                    "core observability contracts contain no "
                    "runtime implementation configuration"
                ),
            ),
        )

    def evaluate_all(
        self,
        snapshot: IntelligenceObservabilitySnapshot,
    ) -> tuple[InvariantEvaluationResult, ...]:
        """Evaluate the full canonical invariant set."""

        if not isinstance(
            snapshot,
            IntelligenceObservabilitySnapshot,
        ):
            raise TypeError("snapshot must be an " "IntelligenceObservabilitySnapshot")

        return tuple(
            self.evaluate(
                invariant,
                snapshot,
            )
            for invariant in self.canonical_invariants()
        )

    @staticmethod
    def _resolve_evaluator(
        invariant_id: str,
    ):
        evaluators = {
            "INV-PROV-001": (IntelligenceInvariantEvaluator._evaluate_provenance),
            "INV-AUTH-001": (
                IntelligenceInvariantEvaluator._evaluate_preserve_authority
            ),
            "INV-AUTH-002": (
                IntelligenceInvariantEvaluator._evaluate_advisory_authority
            ),
            "INV-AUTH-003": (IntelligenceInvariantEvaluator._evaluate_review_authority),
            "INV-STATE-001": (
                IntelligenceInvariantEvaluator._evaluate_adaptation_state
            ),
            "INV-OBS-001": (
                IntelligenceInvariantEvaluator._evaluate_observability_authority
            ),
            "INV-RUNTIME-001": (
                IntelligenceInvariantEvaluator._evaluate_runtime_isolation
            ),
        }

        try:
            return evaluators[invariant_id]
        except KeyError as exc:
            raise ValueError(f"unsupported invariant_id: {invariant_id}") from exc

    @staticmethod
    def _evaluate_provenance(
        snapshot: IntelligenceObservabilitySnapshot,
    ) -> tuple[bool, tuple[str, ...]]:
        objects = (
            snapshot.trace,
            snapshot.summary,
            snapshot.event,
        )

        context_matches = all(obj.context_id == snapshot.context_id for obj in objects)
        correlation_matches = all(
            obj.correlation_id == snapshot.correlation_id for obj in objects
        )
        action_matches = all(obj.action is snapshot.action for obj in objects)

        passed = context_matches and correlation_matches and action_matches

        if passed:
            return (
                True,
                ("provenance is consistent across " "observability state",),
            )

        return (
            False,
            ("provenance mismatch exists across " "observability state",),
        )

    @staticmethod
    def _evaluate_preserve_authority(
        snapshot: IntelligenceObservabilitySnapshot,
    ) -> tuple[bool, tuple[str, ...]]:
        disposition = snapshot.trace.adaptation_explanation.adaptation_disposition

        if disposition is not AdaptationDisposition.PRESERVE:
            return (
                True,
                ("PRESERVE authority invariant is not active " "for this lifecycle",),
            )

        passed = not snapshot.execution_authorized

        return (
            passed,
            (
                (
                    "PRESERVE does not authorize execution"
                    if passed
                    else "PRESERVE incorrectly authorizes execution"
                ),
            ),
        )

    @staticmethod
    def _evaluate_advisory_authority(
        snapshot: IntelligenceObservabilitySnapshot,
    ) -> tuple[bool, tuple[str, ...]]:
        disposition = snapshot.trace.adaptation_explanation.adaptation_disposition

        if disposition is not AdaptationDisposition.ADVISORY:
            return (
                True,
                ("ADVISORY authority invariant is not active " "for this lifecycle",),
            )

        passed = not snapshot.execution_authorized

        return (
            passed,
            (
                (
                    "ADVISORY does not authorize execution"
                    if passed
                    else "ADVISORY incorrectly authorizes execution"
                ),
            ),
        )

    @staticmethod
    def _evaluate_review_authority(
        snapshot: IntelligenceObservabilitySnapshot,
    ) -> tuple[bool, tuple[str, ...]]:
        disposition = snapshot.trace.adaptation_explanation.adaptation_disposition

        if disposition is not AdaptationDisposition.REVIEW:
            return (
                True,
                ("REVIEW authority invariant is not active " "for this lifecycle",),
            )

        passed = not snapshot.execution_authorized

        return (
            passed,
            (
                (
                    "REVIEW does not authorize execution"
                    if passed
                    else "REVIEW incorrectly authorizes execution"
                ),
            ),
        )

    @staticmethod
    def _evaluate_adaptation_state(
        snapshot: IntelligenceObservabilitySnapshot,
    ) -> tuple[bool, tuple[str, ...]]:
        passed = (
            snapshot.historical_influence_applied or not snapshot.adaptation_applied
        )

        return (
            passed,
            (
                (
                    ("adaptation state is consistent with " "historical influence")
                    if passed
                    else ("adaptation is applied without " "historical influence")
                ),
            ),
        )

    @staticmethod
    def _evaluate_observability_authority(
        snapshot: IntelligenceObservabilitySnapshot,
    ) -> tuple[bool, tuple[str, ...]]:
        integration_authority = (
            snapshot.trace.integration_explanation.execution_authorized
        )

        passed = snapshot.execution_authorized is integration_authority

        return (
            passed,
            (
                (
                    ("observability execution authority matches " "integration state")
                    if passed
                    else (
                        "observability execution authority exceeds " "integration state"
                    )
                ),
            ),
        )

    @staticmethod
    def _evaluate_runtime_isolation(
        snapshot: IntelligenceObservabilitySnapshot,
    ) -> tuple[bool, tuple[str, ...]]:
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

        contracts = (
            type(snapshot.trace),
            type(snapshot.summary),
            type(snapshot.event),
            type(snapshot),
        )

        leaked_fields: set[str] = set()

        for contract in contracts:
            names = {field.name for field in fields(contract)}
            leaked_fields.update(names & forbidden)

        if not leaked_fields:
            return (
                True,
                ("observability contracts remain " "runtime-isolated",),
            )

        return (
            False,
            (
                "runtime configuration leaked into "
                "observability contracts: " + ", ".join(sorted(leaked_fields)),
            ),
        )


__all__ = ["IntelligenceInvariantEvaluator"]
