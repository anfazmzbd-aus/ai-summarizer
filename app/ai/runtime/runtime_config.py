"""
AI runtime configuration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AIRuntimeConfig:

    default_temperature: float = 0.2

    default_max_tokens: int = 1024
