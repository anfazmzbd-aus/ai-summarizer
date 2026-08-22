"""
V10 adaptive intelligence policy.

Maps bounded adaptation eligibility and M5 policy context into a deterministic
AdaptationDecision.

M6.4 produces adaptation intent only. It does not execute runtime behavior,
modify TaskDecision, select providers, change strategies, or mutate
configuration.
"""

from __future__ import annotations

from .adaptation_decision import (
    AdaptationDecision,
    AdaptationDisposition,
)
from .adaptation_eligibility import (
    AdaptationEligibility,
    AdaptationEligibilityStatus,
)
from .decision_support_policy import (
    DecisionSupportDisposition,
)
from .experience_informed_decision import (
    ExperienceInformedDecision,
)


class AdaptiveIntelligencePolicy:
    """Apply deterministic bounded adaptation policy."""

    def apply(
        self,
        informed_decision: ExperienceInformedDecision,
        eligibility: AdaptationEligibility,
    ) -> AdaptationDecision:
        """Map eligibility and bounded historical context to adaptation intent."""

        self._validate_inputs(
            informed_decision=informed_decision,
            eligibility=eligibility,
        )

        disposition = self._derive_disposition(
            informed_decision=informed_decision,
            eligibility=eligibility,
        )

        reasons = self._build_reasons(
            informed_decision=informed_decision,
            eligibility=eligibility,
            disposition=disposition,
        )

        return AdaptationDecision.create(
            context_id=informed_decision.decision.context_id,
            correlation_id=informed_decision.decision.correlation_id,
            action=informed_decision.decision.action,
            eligibility_status=eligibility.status,
            disposition=disposition,
            reasons=reasons,
        )

    @staticmethod
    def _validate_inputs(
        *,
        informed_decision: ExperienceInformedDecision,
        eligibility: AdaptationEligibility,
    ) -> None:
        if not isinstance(
            informed_decision,
            ExperienceInformedDecision,
        ):
            raise TypeError(
                "informed_decision must be an " "ExperienceInformedDecision"
            )

        if not isinstance(
            eligibility,
            AdaptationEligibility,
        ):
            raise TypeError("eligibility must be an AdaptationEligibility")

        decision = informed_decision.decision
        policy_result = informed_decision.policy_result

        if decision.context_id != eligibility.context_id:
            raise ValueError("decision and eligibility context_id must match")

        if decision.correlation_id != eligibility.correlation_id:
            raise ValueError("decision and eligibility correlation_id must match")

        if decision.action is not eligibility.action:
            raise ValueError("decision and eligibility action must match")

        if policy_result.disposition is not eligibility.policy_disposition:
            raise ValueError("policy disposition must match eligibility")

        if (
            informed_decision.historical_influence_applied
            is not eligibility.historical_influence_applied
        ):
            raise ValueError("historical influence must match eligibility")

    @staticmethod
    def _derive_disposition(
        *,
        informed_decision: ExperienceInformedDecision,
        eligibility: AdaptationEligibility,
    ) -> AdaptationDisposition:
        if eligibility.status is AdaptationEligibilityStatus.INELIGIBLE:
            return AdaptationDisposition.PRESERVE

        if eligibility.status is AdaptationEligibilityStatus.REVIEW_ONLY:
            return AdaptationDisposition.REVIEW

        policy_disposition = informed_decision.policy_result.disposition

        if policy_disposition is DecisionSupportDisposition.ADVISORY:
            return AdaptationDisposition.ADVISORY

        if policy_disposition is DecisionSupportDisposition.CAUTION:
            return AdaptationDisposition.CONSTRAIN

        if policy_disposition is DecisionSupportDisposition.REVIEW:
            return AdaptationDisposition.REVIEW

        return AdaptationDisposition.PRESERVE

    @staticmethod
    def _build_reasons(
        *,
        informed_decision: ExperienceInformedDecision,
        eligibility: AdaptationEligibility,
        disposition: AdaptationDisposition,
    ) -> tuple[str, ...]:
        reasons: list[str] = list(eligibility.reasons)

        if disposition is AdaptationDisposition.PRESERVE:
            reasons.append("adaptive policy preserves the original decision")

        elif disposition is AdaptationDisposition.ADVISORY:
            reasons.append("adaptive policy allows advisory historical context")

        elif disposition is AdaptationDisposition.CONSTRAIN:
            reasons.append(
                "adaptive policy allows bounded constraint-oriented handling"
            )

        else:
            reasons.append("adaptive policy requires review-oriented handling")

        return tuple(reasons)


__all__ = ["AdaptiveIntelligencePolicy"]
