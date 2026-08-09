"""
AI Summarizer V9.1

OpenAI internal response models.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpenAIResult:
    """
    Normalized OpenAI text result.
    """

    text: str

    model: str | None = None

    usage: dict[str, int] | None = None
