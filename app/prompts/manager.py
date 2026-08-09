"""
AI Summarizer V9.0

Prompt manager.

Coordinates prompt resolution and rendering.
"""

from __future__ import annotations

from .models import PromptDefinition
from .registry import PromptRegistry
from .rendered_prompt import RenderedPrompt
from .renderer import PromptRenderer
from .value_objects import (
    PromptId,
    PromptVersion,
)


class PromptManager:
    """
    High-level prompt orchestration service.
    """

    def __init__(
        self,
        registry: PromptRegistry,
    ) -> None:
        self._registry = registry

    def render(
        self,
        *,
        prompt_id: PromptId,
        version: PromptVersion,
        variables: dict[str, str],
    ) -> RenderedPrompt:
        """
        Resolve and render a prompt.
        """

        prompt = self._registry.resolve(
            prompt_id,
            version,
        )

        return PromptRenderer.render(
            prompt,
            variables,
        )

    def register(
        self,
        prompt: PromptDefinition,
    ) -> None:
        """
        Register a prompt definition.
        """

        self._registry.register(prompt)
