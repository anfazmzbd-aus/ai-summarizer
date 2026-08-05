from app.ai import (
    PromptEngine,
    PromptRegistry,
    PromptRenderer,
    PromptTemplate,
)


def test_prompt_engine():

    registry = PromptRegistry()

    registry.register(
        PromptTemplate(
            name="summary",
            version="1.0",
            template="Summarize {text}",
        )
    )

    engine = PromptEngine(
        registry,
        PromptRenderer(),
    )

    prompt = engine.render(
        "summary",
        text="Document",
    )

    assert prompt == "Summarize Document"
