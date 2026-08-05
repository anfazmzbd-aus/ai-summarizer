"""
Provider abstraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .request import AIRequest
from .response import AIResponse


class AIProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse: ...
