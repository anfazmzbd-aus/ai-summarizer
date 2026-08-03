"""
Composite policy evaluation report.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .decision import PolicyDecision
from .evaluation import PolicyEvaluation


@dataclass(slots=True)
class PolicyReport:

    evaluations: list[PolicyEvaluation] = field(default_factory=list)

    @property
    def decision(self) -> PolicyDecision:

        for evaluation in self.evaluations:
            if evaluation.decision is PolicyDecision.DENY:
                return PolicyDecision.DENY

        return PolicyDecision.ALLOW

    @property
    def allowed(self) -> bool:

        return self.decision is PolicyDecision.ALLOW
