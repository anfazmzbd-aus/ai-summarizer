"""
Composite runtime policy engine.
"""

from __future__ import annotations

from app.distributed.protocols import TaskEnvelope

from .decision import PolicyDecision
from .evaluation import PolicyEvaluation
from .exceptions import PolicyViolation
from .policy import Policy
from .registration import PolicyRegistration
from .report import PolicyReport


class PolicyEngine:

    def __init__(
        self,
        policies: list[Policy] | None = None,
    ) -> None:

        self._policies: list[PolicyRegistration] = []

        if policies:
            for policy in policies:
                self.register(policy)

    def register(
        self,
        policy: Policy,
        priority: int = 100,
    ) -> None:

        self._policies.append(
            PolicyRegistration(
                policy=policy,
                priority=priority,
            )
        )

        self._policies.sort(key=lambda p: p.priority)

    def evaluate_report(
        self,
        task: TaskEnvelope,
    ) -> PolicyReport:

        report = PolicyReport()

        for registration in self._policies:

            result = registration.policy.evaluate(task)

            report.evaluations.append(
                PolicyEvaluation(
                    policy=registration.policy.__class__.__name__,
                    decision=result.decision,
                    reason=result.reason,
                )
            )

            if result.decision is PolicyDecision.DENY:
                break

        return report

    def evaluate(
        self,
        task: TaskEnvelope,
    ) -> None:

        report = self.evaluate_report(task)

        if not report.allowed:

            first = next(
                e for e in report.evaluations if e.decision is PolicyDecision.DENY
            )

            raise PolicyViolation(first.reason)
