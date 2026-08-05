"""
AI provider registry.
"""

from __future__ import annotations

from .provider import AIProvider


class AIProviderRegistry:

    def __init__(self) -> None:

        self._providers: dict[
            str,
            AIProvider,
        ] = {}

    def register(
        self,
        provider: AIProvider,
    ) -> None:

        self._providers[provider.name] = provider

    def get(
        self,
        name: str,
    ) -> AIProvider:

        return self._providers[name]

    def names(
        self,
    ) -> list[str]:

        return sorted(self._providers.keys())
