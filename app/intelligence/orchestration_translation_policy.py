"""
V10 M7 adaptive outcome to orchestration translation policy.

Translates bounded M6 AdaptivePolicyOutcome into an immutable M7
OrchestrationDirective.

M7.2 performs deterministic translation only. It does not execute runtime
behavior, select providers or strategies, modify execution configuration,
or bypass later directive validation.
"""

from __future__ import annotations

from .adaptation_decision import AdaptationDisposition
from .adaptive_policy_outcome import AdaptivePolicyOutcome
from .orchestration_directive import (
    OrchestrationDirective,
    OrchestrationDisposition,
)


class OrchestrationTranslationPolicy:
    """Translate bounded M6 adaptation intent into M7 orchestration intent."""

    def translate(
        self,
        outcome: AdaptivePolicyOutcome,
    ) -> OrchestrationDirective:
        """Translate one adaptive policy outcome deterministically."""

        if not isinstance(outcome, AdaptivePolicyOutcome):
            raise TypeError("outcome must be an AdaptivePolicyOutcome")

        self._validate_outcome(outcome)

        orchestration_disposition = self._derive_orchestration_disposition(
            outcome.adaptation_disposition
        )

        execution_change_allowed = (
            orchestration_disposition is OrchestrationDisposition.BOUNDED_CONSTRAINT
        )

        review_required = (
            orchestration_disposition is OrchestrationDisposition.REVIEW_REQUIRED
        )

        reasons = self._build_reasons(
            outcome=outcome,
            orchestration_disposition=(orchestration_disposition),
        )

        return OrchestrationDirective.create(
            context_id=outcome.context_id,
            correlation_id=outcome.correlation_id,
            action=outcome.action,
            adaptation_disposition=(outcome.adaptation_disposition),
            orchestration_disposition=(orchestration_disposition),
            execution_change_allowed=(execution_change_allowed),
            review_required=review_required,
            reasons=reasons,
        )

    @staticmethod
    def _validate_outcome(
        outcome: AdaptivePolicyOutcome,
    ) -> None:
        decision = outcome.informed_decision.decision

        if outcome.context_id != decision.context_id:
            raise ValueError("outcome context_id must match informed decision")

        if outcome.correlation_id != decision.correlation_id:
            raise ValueError("outcome correlation_id must match informed decision")

        if outcome.action is not decision.action:
            raise ValueError("outcome action must match informed decision")

        if (
            outcome.adaptation_disposition
            is not outcome.adaptation_decision.disposition
        ):
            raise ValueError(
                "outcome adaptation_disposition must match " "adaptation_decision"
            )

        if (
            outcome.adaptation_applied
            is not outcome.adaptation_decision.adaptation_applied
        ):
            raise ValueError(
                "outcome adaptation_applied must match " "adaptation_decision"
            )

    @staticmethod
    def _derive_orchestration_disposition(
        adaptation_disposition: AdaptationDisposition,
    ) -> OrchestrationDisposition:
        if adaptation_disposition is AdaptationDisposition.PRESERVE:
            return OrchestrationDisposition.NO_CHANGE

        if adaptation_disposition is AdaptationDisposition.ADVISORY:
            return OrchestrationDisposition.ADVISORY_CONTEXT

        if adaptation_disposition is AdaptationDisposition.CONSTRAIN:
            return OrchestrationDisposition.BOUNDED_CONSTRAINT

        if adaptation_disposition is AdaptationDisposition.REVIEW:
            return OrchestrationDisposition.REVIEW_REQUIRED

        raise ValueError("unsupported adaptation disposition")

    @staticmethod
    def _build_reasons(
        *,
        outcome: AdaptivePolicyOutcome,
        orchestration_disposition: OrchestrationDisposition,
    ) -> tuple[str, ...]:
        reasons: list[str] = list(outcome.adaptation_decision.reasons)

        if orchestration_disposition is OrchestrationDisposition.NO_CHANGE:
            reasons.append("orchestration preserves existing execution behavior")

        elif orchestration_disposition is OrchestrationDisposition.ADVISORY_CONTEXT:
            reasons.append(
                "orchestration may expose advisory context "
                "without changing execution behavior"
            )

        elif orchestration_disposition is OrchestrationDisposition.BOUNDED_CONSTRAINT:
            reasons.append("orchestration may apply only approved bounded constraints")

        else:
            reasons.append("orchestration requires review-oriented handling")

        return tuple(reasons)


__all__ = ["OrchestrationTranslationPolicy"]
