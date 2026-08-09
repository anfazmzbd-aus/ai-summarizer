"""
AI Summarizer V9.0

Prompt loading utilities.
"""

from __future__ import annotations

from .models import PromptDefinition
from .repository import PromptRepository


class PromptLoader:
    """
    Loads prompt definitions into repositories.
    """

    def __init__(
        self,
        repository: PromptRepository,
    ) -> None:

        self._repository = repository

    def load(
        self,
        prompts: tuple[
            PromptDefinition,
            ...,
        ],
    ) -> int:
        """
        Load multiple prompts.

        Returns number loaded.
        """

        for prompt in prompts:
            self._repository.save(prompt)

        return len(prompts)
