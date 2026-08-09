"""
Prompt renderer.
"""

from __future__ import annotations

import re

from .models import PromptDefinition
from .rendered_prompt import RenderedPrompt
from .validator import PromptValidator

_PATTERN = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class PromptRenderer:
    """
    Renders PromptDefinition instances.
    """

    @staticmethod
    def render(
        prompt: PromptDefinition,
        variables: dict[str, str],
    ) -> RenderedPrompt:

        PromptValidator.validate(
            prompt,
            variables,
        )

        def replace(
            template: str,
        ) -> str:

            def repl(
                match: re.Match[str],
            ) -> str:
                return variables[match.group(1)]

            return _PATTERN.sub(
                repl,
                template,
            )

        return RenderedPrompt(
            system_prompt=replace(prompt.system_template),
            user_prompt=replace(prompt.user_template),
        )
