"""
Policy evaluation result.
"""

from __future__ import annotations

from dataclasses import dataclass

from .decision import PolicyDecision


@dataclass(slots=True, frozen=True)
class PolicyResult:

    decision: PolicyDecision

    reason: str = ""

    @property
    def allowed(self) -> bool:

        return self.decision is PolicyDecision.ALLOW
