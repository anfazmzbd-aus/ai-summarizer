from __future__ import annotations

from enum import Enum


class RuntimeHealth(str, Enum):
    """
    Runtime health classification.
    """

    HEALTHY = "healthy"

    DEGRADED = "degraded"

    FAILED = "failed"
