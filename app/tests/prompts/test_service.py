from app.prompts.models import PromptDefinition, PromptMetadata
from app.prompts.service import PromptService
from app.prompts.value_objects import (
    PromptId,
    PromptVariable,
    PromptVersion,
)


def test_service():

    prompt = PromptDefinition.create(
        metadata=PromptMetadata(
            prompt_id=PromptId("summary"),
            version=PromptVersion(1, 0, 0),
            description="",
            author="system",
        ),
        system_template="System",
        user_template="{{text}}",
        variables=(
            PromptVariable(
                "text",
                "Document",
            ),
        ),
    )

    rendered = PromptService().render(
        prompt,
        {
            "text": "AI Summarizer",
        },
    )

    assert rendered.user_prompt == "AI Summarizer"
