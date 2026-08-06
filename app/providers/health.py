"""
AI Summarizer V9.0

Provider health models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class ProviderStatus(str, Enum):
    """Provider operational state."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(slots=True, frozen=True)
class ProviderHealth:
    """
    Health check result.
    """

    provider: str

    status: ProviderStatus

    latency_ms: float

    checked_at: datetime

    error: str | None = None

    @classmethod
    def healthy(
        cls,
        provider: str,
        latency_ms: float,
    ) -> "ProviderHealth":
        return cls(
            provider=provider,
            status=ProviderStatus.HEALTHY,
            latency_ms=latency_ms,
            checked_at=datetime.now(timezone.utc),
        )

    @classmethod
    def unavailable(
        cls,
        provider: str,
        error: str,
    ) -> "ProviderHealth":
        return cls(
            provider=provider,
            status=ProviderStatus.UNAVAILABLE,
            latency_ms=0.0,
            checked_at=datetime.now(timezone.utc),
            error=error,
        )
