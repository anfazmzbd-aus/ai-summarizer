import pytest

from app.providers.openai.config import (
    OpenAIConfig,
)


def test_config():

    config = OpenAIConfig(
        api_key="test-key",
    )

    assert config.model == "gpt-5"


def test_empty_key():

    with pytest.raises(ValueError):

        OpenAIConfig(
            api_key="",
        )


def test_negative_timeout():

    with pytest.raises(ValueError):

        OpenAIConfig(
            api_key="key",
            timeout=-1,
        )


def test_negative_retries():

    with pytest.raises(ValueError):

        OpenAIConfig(
            api_key="key",
            max_retries=-1,
        )
