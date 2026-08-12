"""
AI Summarizer V9.0

Provider configuration models.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProviderType(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    MOCK = "mock"
    OPENROUTER = "openrouter"


@dataclass(slots=True, frozen=True)
class ProviderConfig:
    """
    Immutable provider configuration.
    """

    provider: ProviderType

    model: str

    api_key: str | None = None

    endpoint: str | None = None

    api_version: str | None = None

    organization: str | None = None

    timeout: float = 60.0

    max_retries: int = 3

    verify_ssl: bool = True
