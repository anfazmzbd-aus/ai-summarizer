from app.providers.request_builder import (
    LLMRequestBuilder,
)

from app.prompts.rendered_prompt import (
    RenderedPrompt,
)


def test_request_builder():

    prompt = RenderedPrompt(
        system_prompt="You summarize",
        user_prompt="Hello",
    )

    request = LLMRequestBuilder.from_prompt(
        prompt,
        "test-model",
    )

    assert request.model == "test-model"

    assert len(request.messages) == 2

    assert request.messages[0].content == "You summarize"
