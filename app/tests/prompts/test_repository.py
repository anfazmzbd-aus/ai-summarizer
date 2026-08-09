from app.prompts.models import (
    PromptDefinition,
    PromptMetadata,
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
            prompt_id=PromptId("summary"),
            version=PromptVersion(
                1,
                0,
                0,
            ),
            description="summary",
            author="system",
        ),
        system_template="system",
        user_template="user",
    )


def test_save_and_get():

    repo = InMemoryPromptRepository()

    prompt = create_prompt()

    repo.save(prompt)

    result = repo.get(
        PromptId("summary"),
        PromptVersion(1, 0, 0),
    )

    assert result == prompt


def test_list_prompts():

    repo = InMemoryPromptRepository()

    repo.save(create_prompt())

    prompts = repo.list_prompts()

    assert prompts == (PromptId("summary"),)
