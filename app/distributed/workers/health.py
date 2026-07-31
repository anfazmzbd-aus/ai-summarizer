"""
AI Summarizer V8.0 Distributed Runtime

Worker health models.
"""

from __future__ import annotations

from enum import Enum


class HealthStatus(str, Enum):
    """
    Worker health state.
    """

    HEALTHY = "healthy"

    DEGRADED = "degraded"

    UNAVAILABLE = "unavailable"
