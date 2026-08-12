import pytest

from app.providers.config import ProviderType
from app.providers.settings import ProviderSettings


def clear_provider_environment(monkeypatch):
    for name in (
        "AI_PROVIDER",
        "AI_MODEL",
        "AI_API_KEY",
        "AI_PROVIDER_ENDPOINT",
        "AI_PROVIDER_ORGANIZATION",
        "AI_PROVIDER_TIMEOUT",
        "AI_PROVIDER_MAX_RETRIES",
    ):
        monkeypatch.delenv(name, raising=False)


def test_default_settings_use_mock(monkeypatch):
    clear_provider_environment(monkeypatch)

    settings = ProviderSettings.from_environment()

    assert settings.provider is ProviderType.MOCK
    assert settings.model == "mock-model"
    assert settings.api_key is None
    assert settings.endpoint is None
    assert settings.organization is None
    assert settings.timeout == 60.0
    assert settings.max_retries == 2


def test_openrouter_configuration(monkeypatch):
    clear_provider_environment(monkeypatch)

    monkeypatch.setenv(
        "AI_PROVIDER",
        "openai",
    )
    monkeypatch.setenv(
        "AI_MODEL",
        "openai/gpt-5-mini",
    )
    monkeypatch.setenv(
        "AI_API_KEY",
        "test-key",
    )
    monkeypatch.setenv(
        "AI_PROVIDER_ENDPOINT",
        "https://openrouter.ai/api/v1",
    )

    settings = ProviderSettings.from_environment()

    assert settings.provider is ProviderType.OPENAI
    assert settings.model == "openai/gpt-5-mini"
    assert settings.api_key == "test-key"
    assert settings.endpoint == "https://openrouter.ai/api/v1"


def test_invalid_provider(monkeypatch):
    clear_provider_environment(monkeypatch)

    monkeypatch.setenv(
        "AI_PROVIDER",
        "invalid-provider",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported AI_PROVIDER",
    ):
        ProviderSettings.from_environment()


def test_empty_model(monkeypatch):
    clear_provider_environment(monkeypatch)

    monkeypatch.setenv(
        "AI_MODEL",
        "   ",
    )

    with pytest.raises(
        ValueError,
        match="AI_MODEL cannot be empty",
    ):
        ProviderSettings.from_environment()


def test_invalid_timeout(monkeypatch):
    clear_provider_environment(monkeypatch)

    monkeypatch.setenv(
        "AI_PROVIDER_TIMEOUT",
        "0",
    )

    with pytest.raises(
        ValueError,
        match="must be positive",
    ):
        ProviderSettings.from_environment()


def test_negative_retries(monkeypatch):
    clear_provider_environment(monkeypatch)

    monkeypatch.setenv(
        "AI_PROVIDER_MAX_RETRIES",
        "-1",
    )

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        ProviderSettings.from_environment()
