"""
AI Summarizer V9.0

Provider exception hierarchy.
"""

from __future__ import annotations


class ProviderError(Exception):
    """
    Base exception for all provider-related errors.
    """


class AuthenticationError(ProviderError):
    """
    Authentication with the provider failed.
    """


class AuthorizationError(ProviderError):
    """
    The authenticated identity is not authorized.
    """


class InvalidRequestError(ProviderError):
    """
    The request sent to the provider is invalid.
    """


class ModelNotFoundError(ProviderError):
    """
    Requested model does not exist.
    """


class RateLimitError(ProviderError):
    """
    Provider rate limit exceeded.
    """


class TimeoutError(ProviderError):
    """
    Provider request timed out.
    """


class ProviderUnavailableError(ProviderError):
    """
    Provider is temporarily unavailable.
    """


class ResponseValidationError(ProviderError):
    """
    Provider returned an invalid response.
    """
