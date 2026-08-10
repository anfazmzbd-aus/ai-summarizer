from app.prompts.models import PromptDefinition
from app.prompts.repository import InMemoryPromptRepository
from app.prompts.registry import PromptRegistry
from app.prompts.manager import PromptManager
from app.prompts.templates.summary import (
    SUMMARY_PROMPT_ID,
    SUMMARY_PROMPT_VERSION,
    build_summary_prompt,
)


def test_summary_prompt_is_versioned():
    prompt = build_summary_prompt()

    assert isinstance(prompt, PromptDefinition)
    assert prompt.metadata.prompt_id == SUMMARY_PROMPT_ID
    assert prompt.metadata.version == SUMMARY_PROMPT_VERSION


def test_summary_prompt_renders_text_variable():
    repository = InMemoryPromptRepository()

    registry = PromptRegistry(repository)
    manager = PromptManager(registry)

    prompt = build_summary_prompt()

    registry.register(prompt)

    rendered = manager.render(
        prompt_id=SUMMARY_PROMPT_ID,
        version=SUMMARY_PROMPT_VERSION,
        variables={
            "text": "Revenue increased by 25 percent.",
        },
    )

    assert rendered.system_prompt
    assert rendered.user_prompt == (
        "Summarize the following text:\n\n" "Revenue increased by 25 percent."
    )


def test_summary_prompt_is_available_from_registry():
    repository = InMemoryPromptRepository()
    registry = PromptRegistry(repository)

    prompt = build_summary_prompt()
    registry.register(prompt)

    assert SUMMARY_PROMPT_ID in registry.available()
