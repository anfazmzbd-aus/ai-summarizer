from app.prompts.models import PromptDefinition, PromptMetadata
from app.prompts.renderer import PromptRenderer
from app.prompts.value_objects import (
    PromptId,
    PromptVariable,
    PromptVersion,
)


def prompt():

    return PromptDefinition.create(
        metadata=PromptMetadata(
            prompt_id=PromptId("summary"),
            version=PromptVersion(1, 0, 0),
            description="",
            author="system",
        ),
        system_template="You summarize.",
        user_template="{{document}}",
        variables=(
            PromptVariable(
                "document",
                "text",
            ),
        ),
    )


def test_render():

    rendered = PromptRenderer.render(
        prompt(),
        {
            "document": "Hello",
        },
    )

    assert rendered.user_prompt == "Hello"
