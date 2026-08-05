from app.config.ai_settings import AISettings


def test_defaults():

    settings = AISettings()

    assert settings.provider
