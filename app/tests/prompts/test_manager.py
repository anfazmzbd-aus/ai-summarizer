from app.prompts.manager import PromptManager
from app.prompts.models import (
    PromptDefinition,
    PromptMetadata,
)
from app.prompts.repository import (
    InMemoryPromptRepository,
)
from app.prompts.registry import (
    PromptRegistry,
)
from app.prompts.value_objects import (
    PromptId,
    PromptVariable,
    PromptVersion,
)


def create_prompt():

    return PromptDefinition.create(
        metadata=PromptMetadata(
            prompt_id=PromptId("summary"),
            version=PromptVersion(
                1,
                0,
                0,
            ),
            description="Summary",
            author="system",
        ),
        system_template="System",
        user_template="{{text}}",
        variables=(
            PromptVariable(
                "text",
                "Input",
            ),
        ),
    )


def test_manager_render():

    registry = PromptRegistry(InMemoryPromptRepository())

    manager = PromptManager(
        registry,
    )

    manager.register(create_prompt())

    rendered = manager.render(
        prompt_id=PromptId(
            "summary",
        ),
        version=PromptVersion(
            1,
            0,
            0,
        ),
        variables={
            "text": "Hello AI",
        },
    )

    assert rendered.user_prompt == "Hello AI"
