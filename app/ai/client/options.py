"""
LLM execution options.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LLMOptions:

    timeout_seconds: float = 30.0

    max_retries: int = 2

    stream: bool = False
