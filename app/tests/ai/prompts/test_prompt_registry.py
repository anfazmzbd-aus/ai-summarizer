from app.ai import (
    PromptRegistry,
    PromptTemplate,
)


def test_prompt_registry():

    registry = PromptRegistry()

    registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Test",
        )
    )

    template = registry.get("summary")

    assert template.template == "Test"
