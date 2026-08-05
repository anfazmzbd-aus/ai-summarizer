"""
Summarization request.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SummarizationRequest:

    text: str

    provider: str

    model: str

    prompt_name: str = "summary"
