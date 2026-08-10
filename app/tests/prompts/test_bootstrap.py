from app.prompts.bootstrap import register_prompt
from app.prompts.models import (
    PromptDefinition,
    PromptMetadata,
)
from app.prompts.repository import InMemoryPromptRepository
from app.prompts.value_objects import (
    PromptId,
    PromptVersion,
)


def test_register_prompt_stores_definition():
    repository = InMemoryPromptRepository()

    prompt_id = PromptId("summary")
    version = PromptVersion(1, 0, 0)

    prompt = PromptDefinition.create(
        metadata=PromptMetadata(
            prompt_id=prompt_id,
            version=version,
            description="Summary prompt",
            author="AI Summarizer",
        ),
        system_template="You are a summarization assistant.",
        user_template="Summarize the following text:\n\n{{text}}",
    )

    result = register_prompt(
        repository,
        prompt,
    )

    assert result is prompt

    stored = repository.get(
        prompt_id,
        version,
    )

    assert stored is prompt
