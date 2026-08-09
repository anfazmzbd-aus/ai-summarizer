"""
Prompt validation.
"""

from __future__ import annotations

import re

from .exceptions import PromptValidationError
from .models import PromptDefinition

_PATTERN = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class PromptValidator:
    """
    Validates prompt rendering inputs.
    """

    @staticmethod
    def validate(
        prompt: PromptDefinition,
        variables: dict[str, str],
    ) -> None:

        required = {variable.name for variable in prompt.variables if variable.required}

        missing = required.difference(variables)

        if missing:
            raise PromptValidationError(
                "Missing variables: " + ", ".join(sorted(missing))
            )

        templates = (
            prompt.system_template,
            prompt.user_template,
        )

        placeholders: set[str] = set()

        for template in templates:
            placeholders.update(_PATTERN.findall(template))

        undefined = placeholders.difference(variables)

        if undefined:
            raise PromptValidationError(
                "Undefined variables: " + ", ".join(sorted(undefined))
            )
