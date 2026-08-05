"""
Prompt renderer.
"""

from __future__ import annotations

from .prompt_template import PromptTemplate


class PromptRenderer:

    def render(
        self,
        template: PromptTemplate,
        **variables,
    ) -> str:

        return template.template.format(**variables)
