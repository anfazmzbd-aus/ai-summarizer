"""
Prompt service.
"""

from __future__ import annotations

from .models import PromptDefinition
from .rendered_prompt import RenderedPrompt
from .renderer import PromptRenderer


class PromptService:
    """
    High-level prompt rendering service.
    """

    def render(
        self,
        prompt: PromptDefinition,
        variables: dict[str, str],
    ) -> RenderedPrompt:

        return PromptRenderer.render(
            prompt,
            variables,
        )
