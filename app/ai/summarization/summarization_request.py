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

    prompt_version: str = "1.0"

    summary_instruction: str = (
        "Provide a balanced summary of the important information."
    )

    length_instruction: str = (
        "Produce a balanced summary covering the principal information and "
        "important supporting context."
    )

    additional_instruction: str = "No additional instructions."
