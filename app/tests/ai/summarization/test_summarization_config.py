from app.ai import SummarizationConfig


def test_config():

    config = SummarizationConfig()

    assert config.default_prompt == "summary"
