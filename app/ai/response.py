"""
AI response model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AIResponse:

    text: str

    model: str

    prompt_tokens: int = 0

    completion_tokens: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:

        return self.prompt_tokens + self.completion_tokens
