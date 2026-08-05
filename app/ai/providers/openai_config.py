"""
OpenAI provider configuration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OpenAIConfig:

    api_key: str

    model: str

    base_url: str | None = None

    organization: str | None = None

    timeout: float = 30.0
