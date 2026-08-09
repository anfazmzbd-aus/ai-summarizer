"""
AI Summarizer V9.1

Provider response normalization helpers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.providers.models import LLMResponse


class ResponseParser(ABC):
    """
    Converts provider responses into
    canonical LLMResponse objects.
    """

    @abstractmethod
    def parse(
        self,
        response: object,
    ) -> LLMResponse:
        raise NotImplementedError
