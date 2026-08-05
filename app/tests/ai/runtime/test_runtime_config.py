from app.ai import AIRuntimeConfig


def test_runtime_config():

    config = AIRuntimeConfig()

    assert config.default_temperature == 0.2
    assert config.default_max_tokens == 1024
