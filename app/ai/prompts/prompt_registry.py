"""
Prompt registry.
"""

from __future__ import annotations

from .prompt_template import PromptTemplate


class PromptRegistry:

    def __init__(self) -> None:

        self._templates: dict[
            str,
            PromptTemplate,
        ] = {}

    def register(
        self,
        template: PromptTemplate,
    ) -> None:

        key = f"{template.name}:{template.version}"

        self._templates[key] = template

    def get(
        self,
        name: str,
        version: str = "1.0",
    ) -> PromptTemplate:

        return self._templates[f"{name}:{version}"]
