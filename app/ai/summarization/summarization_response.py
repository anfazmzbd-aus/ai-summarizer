"""
Summarization response.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SummarizationResponse:

    summary: str

    prompt: str

    model: str

    prompt_tokens: int

    completion_tokens: int

    @property
    def total_tokens(self) -> int:

        return self.prompt_tokens + self.completion_tokens
