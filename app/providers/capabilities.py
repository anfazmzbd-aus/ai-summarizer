"""
AI Summarizer V9.1

Provider capability definitions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    """
    Supported provider features.
    """

    streaming: bool = False

    vision: bool = False

    tool_calling: bool = False

    structured_output: bool = False

    embeddings: bool = False

    audio: bool = False

    reasoning: bool = False
