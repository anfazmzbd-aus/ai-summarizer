"""
Supported AI providers.
"""

from __future__ import annotations

from enum import Enum


class ProviderType(str, Enum):

    OPENAI = "openai"

    AZURE_OPENAI = "azure_openai"

    OLLAMA = "ollama"

    FAKE = "fake"
