"""
Provider configuration factory.
"""

from __future__ import annotations

from .config import ProviderConfig


class ProviderFactory:

    def create_config(
        self,
        provider,
        model: str,
        **kwargs,
    ) -> ProviderConfig:

        return ProviderConfig(
            provider=provider,
            model=model,
            **kwargs,
        )
