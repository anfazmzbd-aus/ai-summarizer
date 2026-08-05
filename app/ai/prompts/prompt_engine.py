"""
Prompt engine.
"""

from __future__ import annotations

from .prompt_registry import PromptRegistry
from .prompt_renderer import PromptRenderer


class PromptEngine:

    def __init__(
        self,
        registry: PromptRegistry,
        renderer: PromptRenderer,
    ) -> None:

        self._registry = registry
        self._renderer = renderer

    def render(
        self,
        name: str,
        *,
        version: str = "1.0",
        **variables,
    ) -> str:

        template = self._registry.get(
            name,
            version,
        )

        return self._renderer.render(
            template,
            **variables,
        )
