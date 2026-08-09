"""
AI Summarizer V9.1

Provider metadata.
"""

from __future__ import annotations

from dataclasses import dataclass

from .capabilities import ProviderCapabilities


@dataclass(frozen=True, slots=True)
class ProviderInfo:
    """
    Describes a provider installation.
    """

    name: str

    default_model: str

    models: tuple[str, ...]

    capabilities: ProviderCapabilities

    api_version: str | None = None
