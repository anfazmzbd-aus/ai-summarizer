"""
V10 adaptation eligibility evaluator.

Deterministically evaluates whether an ExperienceInformedDecision is
eligible for later bounded adaptation.

M6.2 performs eligibility evaluation only. It does not create adaptation
instructions, modify TaskDecision, invoke runtime behavior, or select
providers/strategies.
"""

from __future__ import annotations

from .adaptation_eligibility import (
    AdaptationEligibility,
    AdaptationEligibilityStatus,
)
from .decision_support_policy import (
    DecisionSupportDisposition,
)
from .experience_evidence import EvidenceStrength
from .experience_informed_decision import (
    ExperienceInformedDecision,
)


class AdaptationEligibilityEvaluator:
    """Evaluate bounded adaptation eligibility."""

    def evaluate(
        self,
        informed_decision: ExperienceInformedDecision,
    ) -> AdaptationEligibility:
        """Return deterministic adaptation eligibility."""

        if not isinstance(
            informed_decision,
            ExperienceInformedDecision,
        ):
            raise TypeError(
                "informed_decision must be an " "ExperienceInformedDecision"
            )

        self._validate_consistency(informed_decision)

        policy_result = informed_decision.policy_result

        status = self._derive_status(informed_decision)

        reasons = self._build_reasons(
            informed_decision=informed_decision,
            status=status,
        )

        return AdaptationEligibility.create(
            context_id=informed_decision.decision.context_id,
            correlation_id=(informed_decision.decision.correlation_id),
            action=informed_decision.decision.action,
            policy_disposition=(policy_result.disposition),
            historical_influence_applied=(
                informed_decision.historical_influence_applied
            ),
            status=status,
            reasons=reasons,
        )

    @staticmethod
    def _validate_consistency(
        informed_decision: ExperienceInformedDecision,
    ) -> None:
        decision = informed_decision.decision
        policy_result = informed_decision.policy_result

        if decision.context_id != policy_result.context_id:
            raise ValueError("decision and policy_result context_id must match")

        if decision.correlation_id != policy_result.correlation_id:
            raise ValueError("decision and policy_result correlation_id must match")

        if decision.action is not policy_result.action:
            raise ValueError("decision and policy_result action must match")

        if (
            informed_decision.historical_influence_applied
            is not policy_result.historical_influence_allowed
        ):
            raise ValueError("historical influence must match policy result")

    @staticmethod
    def _derive_status(
        informed_decision: ExperienceInformedDecision,
    ) -> AdaptationEligibilityStatus:
        policy_result = informed_decision.policy_result

        if not informed_decision.historical_influence_applied:
            return AdaptationEligibilityStatus.INELIGIBLE

        if policy_result.evidence_strength is not EvidenceStrength.ESTABLISHED:
            return AdaptationEligibilityStatus.INELIGIBLE

        if policy_result.disposition is DecisionSupportDisposition.PRESERVE:
            return AdaptationEligibilityStatus.INELIGIBLE

        if policy_result.disposition is DecisionSupportDisposition.REVIEW:
            return AdaptationEligibilityStatus.REVIEW_ONLY

        return AdaptationEligibilityStatus.ELIGIBLE

    @staticmethod
    def _build_reasons(
        *,
        informed_decision: ExperienceInformedDecision,
        status: AdaptationEligibilityStatus,
    ) -> tuple[str, ...]:
        reasons: list[str] = list(informed_decision.reasons)

        policy_result = informed_decision.policy_result

        if not informed_decision.historical_influence_applied:
            reasons.append(
                "historical influence is not applied, " "so adaptation is ineligible"
            )

        elif policy_result.evidence_strength is not EvidenceStrength.ESTABLISHED:
            reasons.append(
                "historical evidence is not established enough "
                "for adaptation eligibility"
            )

        elif status is AdaptationEligibilityStatus.REVIEW_ONLY:
            reasons.append(
                "adverse historical evidence permits review-only " "adaptation handling"
            )

        elif status is AdaptationEligibilityStatus.ELIGIBLE:
            reasons.append(
                "bounded historical influence is eligible for "
                "adaptive policy evaluation"
            )

        else:
            reasons.append(
                "adaptation is not permitted under the current "
                "bounded policy disposition"
            )

        return tuple(reasons)


__all__ = ["AdaptationEligibilityEvaluator"]
