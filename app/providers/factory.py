"""
AI Summarizer V9.0

Provider factory.

Creates provider instances from configuration.
"""

from __future__ import annotations

from collections.abc import Callable

from .base import BaseProvider
from .config import ProviderConfig, ProviderType
from .exceptions import ProviderError


ProviderCreator = Callable[[ProviderConfig], BaseProvider]


class ProviderFactory:
    """
    Creates providers based on provider configuration.
    """

    def __init__(self) -> None:
        self._creators: dict[
            ProviderType,
            ProviderCreator,
        ] = {}

    def register(
        self,
        provider_type: ProviderType,
        creator: ProviderCreator,
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Register a provider creator.
        """

        if provider_type in self._creators and not overwrite:
            raise ValueError(f"Creator already registered: {provider_type}")

        self._creators[provider_type] = creator

    def create(
        self,
        config: ProviderConfig,
    ) -> BaseProvider:
        """
        Create provider from configuration.
        """

        try:
            creator = self._creators[config.provider]
        except KeyError as exc:
            raise ProviderError(f"No provider registered: {config.provider}") from exc

        return creator(config)

    def supported_providers(self) -> tuple[ProviderType, ...]:
        """
        Return supported provider types.
        """

        return tuple(self._creators.keys())
