"""
Policy registration.
"""

from __future__ import annotations

from dataclasses import dataclass

from .policy import Policy


@dataclass(slots=True)
class PolicyRegistration:

    policy: Policy

    priority: int = 100
