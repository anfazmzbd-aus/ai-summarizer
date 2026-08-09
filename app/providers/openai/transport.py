"""
OpenAI transport layer.

Owns SDK communication only.
"""

from __future__ import annotations

from openai import OpenAI

from .config import OpenAIConfig


class OpenAITransport:
    """
    Thin wrapper around the official SDK.
    """

    def __init__(
        self,
        config: OpenAIConfig,
    ) -> None:

        self._config = config

        self._client = OpenAI(
            api_key=config.api_key,
            organization=config.organization,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    @property
    def client(self) -> OpenAI:
        return self._client
