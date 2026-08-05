from app.ai import (
    PromptRenderer,
    PromptTemplate,
)


def test_prompt_renderer():

    renderer = PromptRenderer()

    template = PromptTemplate(
        name="summary",
        version="1.0",
        template="Hello {name}",
    )

    assert (
        renderer.render(
            template,
            name="World",
        )
        == "Hello World"
    )
