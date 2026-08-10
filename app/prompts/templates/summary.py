"""
AI Summarizer V9.x

Production summary prompt definition.
"""

from __future__ import annotations

from app.prompts.models import (
    PromptDefinition,
    PromptMetadata,
)
from app.prompts.value_objects import (
    PromptId,
    PromptVariable,
    PromptVersion,
)


SUMMARY_PROMPT_ID = PromptId("summary")
SUMMARY_PROMPT_VERSION = PromptVersion(1, 0, 0)


def build_summary_prompt() -> PromptDefinition:
    """
    Build the production summary prompt.

    The prompt is deliberately deterministic and versioned.
    """

    return PromptDefinition.create(
        metadata=PromptMetadata(
            prompt_id=SUMMARY_PROMPT_ID,
            version=SUMMARY_PROMPT_VERSION,
            description="Production summary generation prompt.",
            author="AI Summarizer",
            tags=("summary", "production", "v9"),
        ),
        system_template=(
            "You are a professional summarization assistant. "
            "Produce a concise, accurate summary of the supplied text. "
            "Preserve important facts and avoid introducing information "
            "not present in the source."
        ),
        user_template=("Summarize the following text:\n\n" "{{text}}"),
        variables=(
            PromptVariable(
                name="text",
                description="Source text to summarize.",
                required=True,
            ),
        ),
    )
