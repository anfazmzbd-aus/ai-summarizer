from app.prompts.models import (
    PromptDefinition,
    PromptMetadata,
)

from app.prompts.registry import (
    PromptRegistry,
)

from app.prompts.repository import (
    InMemoryPromptRepository,
)

from app.prompts.value_objects import (
    PromptId,
    PromptVersion,
)


def create_prompt():

    return PromptDefinition.create(
        metadata=PromptMetadata(
            prompt_id=PromptId("test"),
            version=PromptVersion(1, 0, 0),
            description="test",
            author="system",
        ),
        system_template="system",
        user_template="user",
    )


def test_register_and_resolve():

    registry = PromptRegistry(InMemoryPromptRepository())

    registry.register(create_prompt())

    result = registry.resolve(
        PromptId("test"),
        PromptVersion(1, 0, 0),
    )

    assert result.metadata.prompt_id.value == "test"


def test_available():

    registry = PromptRegistry(InMemoryPromptRepository())

    registry.register(create_prompt())

    assert len(registry.available()) == 1
