"""
AI request model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AIRequest:

    prompt: str

    model: str

    temperature: float = 0.2

    max_tokens: int = 1024

    metadata: dict[str, Any] = field(default_factory=dict)
