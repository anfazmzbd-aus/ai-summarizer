"""
Individual policy evaluation result.
"""

from __future__ import annotations

from dataclasses import dataclass

from .decision import PolicyDecision


@dataclass(slots=True, frozen=True)
class PolicyEvaluation:

    policy: str

    decision: PolicyDecision

    reason: str = ""
