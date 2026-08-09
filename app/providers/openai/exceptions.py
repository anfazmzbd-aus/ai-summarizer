"""
AI Summarizer V9.1

OpenAI provider exceptions.
"""

from __future__ import annotations


class OpenAIProviderError(Exception):
    """Base OpenAI provider exception."""


class OpenAIAuthenticationError(OpenAIProviderError):
    """Authentication failed."""


class OpenAIRateLimitError(OpenAIProviderError):
    """Rate limit exceeded."""


class OpenAITimeoutError(OpenAIProviderError):
    """Provider timeout."""


class OpenAIExecutionError(OpenAIProviderError):
    """Unexpected provider execution failure."""
