"""
AI exceptions.
"""


class AIProviderError(Exception):
    """Base AI provider error."""


class ModelNotFoundError(AIProviderError):
    """Requested model unavailable."""


class AIRequestError(AIProviderError):
    """Invalid AI request."""
