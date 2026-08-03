"""
Policy decision types.
"""

from __future__ import annotations

from enum import Enum


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
