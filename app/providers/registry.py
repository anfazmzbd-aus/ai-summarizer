"""
AI Summarizer V9.0

Provider registry.

Maintains provider implementations available
to the runtime.
"""

from __future__ import annotations

from threading import RLock

from .base import BaseProvider


class ProviderRegistry:
    """
    Thread-safe provider registry.
    """

    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}
        self._lock = RLock()

    def register(
        self,
        name: str,
        provider: BaseProvider,
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Register a provider instance.
        """

        with self._lock:
            if name in self._providers and not overwrite:
                raise ValueError(f"Provider already registered: {name}")

            self._providers[name] = provider

    def get(
        self,
        name: str,
    ) -> BaseProvider:
        """
        Retrieve a provider.
        """

        with self._lock:
            try:
                return self._providers[name]
            except KeyError as exc:
                raise KeyError(f"Provider not found: {name}") from exc

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider.
        """

        with self._lock:
            self._providers.pop(name, None)

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check provider availability.
        """

        with self._lock:
            return name in self._providers

    def list_providers(self) -> tuple[str, ...]:
        """
        Return registered provider names.
        """

        with self._lock:
            return tuple(self._providers.keys())
