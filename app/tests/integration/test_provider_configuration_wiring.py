from unittest.mock import Mock, patch

from app.providers.config import ProviderType
from app.providers.settings import ProviderSettings
from app.services.summarize_service import SummarizeService


def test_settings_to_summarize_service_mock_wiring():
    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="configured-mock",
    )

    service = SummarizeService(
        provider_settings=settings,
    )

    assert service._provider_settings is settings
    assert service._model == "configured-mock"
    assert service._llm_service.provider_name == "mock"


def test_settings_runtime_reaches_application_service():
    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="configured-model",
    )

    service = SummarizeService(
        provider_settings=settings,
    )

    result = service.run(
        "Configuration wiring validation.",
    )

    assert result.status == "success"
    assert result.result["summary"] == ("Mock response generated successfully.")


def test_explicit_llm_service_has_precedence_over_settings():
    llm_service = Mock()

    settings = ProviderSettings(
        provider=ProviderType.MOCK,
        model="settings-model",
    )

    service = SummarizeService(
        llm_service=llm_service,
        provider_settings=settings,
    )

    assert service._llm_service is llm_service


def test_openrouter_factory_path_is_preserved():
    with patch("app.providers.openai.provider.OpenAITransport") as transport_class:
        transport_class.return_value = Mock()

        service = SummarizeService.from_openrouter(
            api_key="test-key",
            model="openai/gpt-5-mini",
        )

    assert service._llm_service is not None
    assert service._model == "openai/gpt-5-mini"
