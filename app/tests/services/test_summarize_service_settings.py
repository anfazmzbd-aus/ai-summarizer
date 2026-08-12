from unittest.mock import Mock

from app.providers.config import ProviderType
from app.providers.settings import ProviderSettings
from app.services.llm_service import LLMService
from app.services.summarize_service import SummarizeService


def test_summarize_service_accepts_provider_settings():
    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="settings-model",
    )

    service = SummarizeService(
        provider_settings=settings,
    )

    assert service._provider_settings is settings
    assert service._llm_service is not None
    assert service._model == "settings-model"


def test_summarize_service_uses_settings_runtime():
    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="settings-model",
    )

    service = SummarizeService(
        provider_settings=settings,
    )

    result = service.run(
        "Revenue increased.",
    )

    assert result["summary"] == ("Mock response generated successfully.")

    assert result.result["summary"] == ("Mock response generated successfully.")


def test_summarize_service_preserves_explicit_llm_service():
    llm_service = Mock(spec=LLMService)

    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="settings-model",
    )

    service = SummarizeService(
        llm_service=llm_service,
        provider_settings=settings,
    )

    assert service._llm_service is llm_service
    assert service._provider_settings is settings


def test_summarize_service_defaults_to_mock_without_settings():
    service = SummarizeService()

    result = service.run(
        "Production deployment completed successfully.",
    )

    assert result["summary"] == ("Mock response generated successfully.")

    assert result.metadata["version"] == "v7.7"


def test_summarize_service_from_environment_mock(
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_PROVIDER",
        "mock",
    )
    monkeypatch.setenv(
        "AI_MODEL",
        "environment-model",
    )

    service = SummarizeService.from_environment()

    assert service._provider_settings is not None
    assert service._provider_settings.provider is ProviderType.MOCK
    assert service._provider_settings.model == ("environment-model")

    result = service.run(
        "Environment configuration test.",
    )

    assert result["summary"] == ("Mock response generated successfully.")


def test_summarize_service_from_environment_rejects_invalid_provider(
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_PROVIDER",
        "unsupported-provider",
    )

    try:
        SummarizeService.from_environment()
    except ValueError as exc:
        assert str(exc) == ("Unsupported AI_PROVIDER: unsupported-provider")
    else:
        raise AssertionError("Expected ValueError for unsupported provider")
