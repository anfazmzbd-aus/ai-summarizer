"""
AI provider configuration.
"""

from __future__ import annotations

from dataclasses import dataclass

from .provider_type import ProviderType


@dataclass(slots=True)
class ProviderConfig:

    provider: ProviderType

    model: str

    api_key: str | None = None

    endpoint: str | None = None

    timeout_seconds: float = 30.0
