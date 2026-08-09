"""
AI Summarizer V9.0

Prompt domain exceptions.
"""

from __future__ import annotations


class PromptError(Exception):
    """
    Base prompt exception.
    """


class InvalidPromptError(PromptError):
    """
    Invalid prompt definition.
    """


class PromptNotFoundError(PromptError):
    """
    Prompt does not exist.
    """


class PromptVersionError(PromptError):
    """
    Invalid prompt version.
    """


class PromptValidationError(PromptError):
    """
    Prompt validation failure.
    """
