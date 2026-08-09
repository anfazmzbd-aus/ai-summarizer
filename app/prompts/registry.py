"""
AI Summarizer V9.0

Prompt registry.

Runtime-facing prompt discovery layer.
"""

from __future__ import annotations

from .models import PromptDefinition
from .repository import PromptRepository
from .value_objects import (
    PromptId,
    PromptVersion,
)


class PromptRegistry:
    """
    Provides prompt lookup services.
    """

    def __init__(
        self,
        repository: PromptRepository,
    ) -> None:

        self._repository = repository

    def register(
        self,
        prompt: PromptDefinition,
    ) -> None:

        self._repository.save(prompt)

    def resolve(
        self,
        prompt_id: PromptId,
        version: PromptVersion,
    ) -> PromptDefinition:

        return self._repository.get(
            prompt_id,
            version,
        )

    def available(
        self,
    ) -> tuple[PromptId, ...]:

        return self._repository.list_prompts()
