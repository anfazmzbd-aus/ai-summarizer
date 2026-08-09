"""
AI Summarizer V9.1

OpenAI SDK wrapper.

SDK dependency isolation layer.
"""

from __future__ import annotations


class OpenAIClient:
    """
    Wrapper around OpenAI SDK client.

    Actual SDK initialization will happen
    during live integration.
    """

    def __init__(
        self,
        config,
    ) -> None:

        self.config = config

        self._client = None

    @property
    def client(self):
        """
        Access underlying SDK client.
        """

        return self._client
