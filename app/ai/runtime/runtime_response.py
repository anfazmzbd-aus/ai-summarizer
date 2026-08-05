"""
AI runtime response.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.ai import AIResponse


@dataclass(slots=True)
class AIRuntimeResponse:

    prompt: str

    response: AIResponse
