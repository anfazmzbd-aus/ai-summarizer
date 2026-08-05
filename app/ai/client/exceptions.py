"""
LLM client exceptions.
"""


class LLMClientError(Exception):
    """Base client error."""


class LLMTimeoutError(LLMClientError):
    """Timeout occurred."""
