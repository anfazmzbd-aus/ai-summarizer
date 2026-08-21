"""
V10 experience-informed decision boundary.

Composes an immutable TaskDecision with an immutable
DecisionSupportPolicyResult into a bounded intelligence result.

M5.5 preserves the original decision and records whether historical
experience was permitted to influence its interpretation. It does not
replace decisions, execute runtime behavior, retry, replan, select
providers, or alter strategies.
"""

from __future__ import annotations

from dataclasses import dataclass

from .decision_support_policy import (
    DecisionSupportDisposition,
    DecisionSupportPolicyResult,
)
from .task_decision import TaskDecision


@dataclass(frozen=True, slots=True)
class ExperienceInformedDecision:
    """
    Immutable composition of the original decision and bounded policy result.

    The original TaskDecision remains authoritative and unchanged.
    """

    decision: TaskDecision
    policy_result: DecisionSupportPolicyResult
    historical_influence_applied: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.decision, TaskDecision):
            raise TypeError("decision must be a TaskDecision")

        if not isinstance(
            self.policy_result,
            DecisionSupportPolicyResult,
        ):
            raise TypeError("policy_result must be a DecisionSupportPolicyResult")

        if self.decision.context_id != self.policy_result.context_id:
            raise ValueError("decision and policy_result context_id must match")

        if self.decision.correlation_id != self.policy_result.correlation_id:
            raise ValueError("decision and policy_result correlation_id must match")

        if self.decision.action is not self.policy_result.action:
            raise ValueError("decision and policy_result action must match")

        if not isinstance(
            self.historical_influence_applied,
            bool,
        ):
            raise TypeError("historical_influence_applied must be a bool")

        if (
            self.historical_influence_applied
            is not self.policy_result.historical_influence_allowed
        ):
            raise ValueError("historical_influence_applied must match policy_result")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

    @classmethod
    def create(
        cls,
        *,
        decision: TaskDecision,
        policy_result: DecisionSupportPolicyResult,
        reasons: tuple[str, ...],
    ) -> "ExperienceInformedDecision":
        """Create a bounded experience-informed decision."""

        return cls(
            decision=decision,
            policy_result=policy_result,
            historical_influence_applied=(policy_result.historical_influence_allowed),
            reasons=reasons,
        )


class ExperienceInformedDecisionBoundary:
    """
    Compose current decision with bounded historical policy influence.

    The boundary validates identity consistency and produces a new immutable
    composition object while preserving the original TaskDecision unchanged.
    """

    def compose(
        self,
        decision: TaskDecision,
        policy_result: DecisionSupportPolicyResult,
    ) -> ExperienceInformedDecision:
        """Compose a deterministic experience-informed decision result."""

        if not isinstance(decision, TaskDecision):
            raise TypeError("decision must be a TaskDecision")

        if not isinstance(
            policy_result,
            DecisionSupportPolicyResult,
        ):
            raise TypeError("policy_result must be a DecisionSupportPolicyResult")

        self._validate_identity(
            decision=decision,
            policy_result=policy_result,
        )

        reasons = self._build_reasons(
            policy_result=policy_result,
        )

        return ExperienceInformedDecision.create(
            decision=decision,
            policy_result=policy_result,
            reasons=reasons,
        )

    @staticmethod
    def _validate_identity(
        *,
        decision: TaskDecision,
        policy_result: DecisionSupportPolicyResult,
    ) -> None:
        if decision.context_id != policy_result.context_id:
            raise ValueError("decision and policy_result context_id must match")

        if decision.correlation_id != policy_result.correlation_id:
            raise ValueError("decision and policy_result correlation_id must match")

        if decision.action is not policy_result.action:
            raise ValueError("decision and policy_result action must match")

    @staticmethod
    def _build_reasons(
        *,
        policy_result: DecisionSupportPolicyResult,
    ) -> tuple[str, ...]:
        reasons: list[str] = list(policy_result.reasons)

        if policy_result.disposition is DecisionSupportDisposition.PRESERVE:
            reasons.append(
                "the original decision is preserved without historical influence"
            )

        elif policy_result.disposition is DecisionSupportDisposition.ADVISORY:
            reasons.append("historical experience is applied as advisory context")

        elif policy_result.disposition is DecisionSupportDisposition.CAUTION:
            reasons.append("historical experience is applied as cautionary context")

        else:
            reasons.append("historical experience is applied as review context")

        return tuple(reasons)


__all__ = [
    "ExperienceInformedDecision",
    "ExperienceInformedDecisionBoundary",
]
