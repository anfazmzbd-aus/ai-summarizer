from app.ai import LLMOptions


def test_options():

    options = LLMOptions()

    assert options.timeout_seconds == 30.0
    assert options.max_retries == 2
    assert options.stream is False
