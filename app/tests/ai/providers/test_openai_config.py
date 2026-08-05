from app.ai import OpenAIConfig


def test_openai_config():

    config = OpenAIConfig(
        api_key="abc",
        model="gpt-5-mini",
    )

    assert config.model == "gpt-5-mini"
