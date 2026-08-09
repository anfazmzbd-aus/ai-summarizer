"""
AI Summarizer V9.1

Canonical LLM request builder.
"""

from __future__ import annotations

from app.providers.models import (
    LLMMessage,
    LLMRequest,
    MessageRole,
)

from app.prompts.rendered_prompt import (
    RenderedPrompt,
)


class LLMRequestBuilder:
    """
    Builds provider-independent LLM requests.
    """

    @staticmethod
    def from_prompt(
        prompt: RenderedPrompt,
        model: str,
    ) -> LLMRequest:

        return LLMRequest(
            model=model,
            messages=(
                LLMMessage(
                    role=MessageRole.SYSTEM,
                    content=prompt.system_prompt,
                ),
                LLMMessage(
                    role=MessageRole.USER,
                    content=prompt.user_prompt,
                ),
            ),
        )
