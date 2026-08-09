"""
AI Summarizer V9.0

Prompt repository abstraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import PromptDefinition
from .value_objects import PromptId, PromptVersion


class PromptRepository(ABC):
    """
    Storage contract for prompts.
    """

    @abstractmethod
    def save(
        self,
        prompt: PromptDefinition,
    ) -> None:
        """
        Store a prompt definition.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        prompt_id: PromptId,
        version: PromptVersion,
    ) -> PromptDefinition:
        """
        Retrieve a specific prompt version.
        """
        raise NotImplementedError

    @abstractmethod
    def list_prompts(
        self,
    ) -> tuple[PromptId, ...]:
        """
        List available prompts.
        """
        raise NotImplementedError


class InMemoryPromptRepository(PromptRepository):
    """
    Development repository.

    Used until persistent storage is introduced.
    """

    def __init__(self) -> None:

        self._prompts: dict[
            tuple[str, str],
            PromptDefinition,
        ] = {}

    def save(
        self,
        prompt: PromptDefinition,
    ) -> None:

        key = (
            prompt.metadata.prompt_id.value,
            str(prompt.metadata.version),
        )

        self._prompts[key] = prompt

    def get(
        self,
        prompt_id: PromptId,
        version: PromptVersion,
    ) -> PromptDefinition:

        key = (
            prompt_id.value,
            str(version),
        )

        return self._prompts[key]

    def list_prompts(
        self,
    ) -> tuple[PromptId, ...]:

        values = {key[0] for key in self._prompts}

        return tuple(PromptId(value) for value in values)
