from app.prompts.rendered_prompt import RenderedPrompt


def test_messages():

    prompt = RenderedPrompt(
        system_prompt="system",
        user_prompt="user",
    )

    assert prompt.messages() == (
        "system",
        "user",
    )
