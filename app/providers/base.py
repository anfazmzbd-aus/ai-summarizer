"""
AI Summarizer V9.0

Abstract provider contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import LLMRequest, LLMResponse
from .health import ProviderHealth


class BaseProvider(ABC):
    """
    Base contract implemented by every LLM provider.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Provider name.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """
        Whether the provider supports streaming responses.
        """
        raise NotImplementedError

    @abstractmethod
    def chat(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Execute a chat completion request.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> ProviderHealth:
        """
        Verify provider availability.
        """
        raise NotImplementedError

    @abstractmethod
    def available_models(self) -> tuple[str, ...]:
        """
        Return supported model identifiers.
        """
        raise NotImplementedError
