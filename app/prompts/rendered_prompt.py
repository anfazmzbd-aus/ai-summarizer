"""
Rendered prompt models.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RenderedPrompt:
    """
    Final prompt sent to an LLM.
    """

    system_prompt: str

    user_prompt: str

    def messages(self) -> tuple[str, str]:
        """
        Return prompts in execution order.
        """
        return (
            self.system_prompt,
            self.user_prompt,
        )
