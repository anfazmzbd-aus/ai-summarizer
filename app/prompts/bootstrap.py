"""
AI Summarizer V9.x

Prompt bootstrap utilities.

Provides deterministic registration of prompt definitions into the
configured prompt repository.
"""

from __future__ import annotations

from .models import PromptDefinition
from .repository import PromptRepository


def register_prompt(
    repository: PromptRepository,
    prompt: PromptDefinition,
) -> PromptDefinition:
    """
    Register a prompt definition and return the registered definition.

    The repository remains responsible for persistence while this helper
    provides a small, explicit bootstrap boundary.
    """

    repository.save(prompt)

    return prompt
