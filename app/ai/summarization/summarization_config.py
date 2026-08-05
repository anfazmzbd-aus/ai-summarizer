"""
Summarization configuration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SummarizationConfig:

    default_prompt: str = "summary"
