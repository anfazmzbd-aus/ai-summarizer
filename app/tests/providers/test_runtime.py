from app.providers.config import (
    ProviderConfig,
    ProviderType,
)
from app.providers.factory import ProviderFactory
from app.providers.mock_provider import MockProvider
from app.providers.runtime import ProviderRuntime


def build_factory() -> ProviderFactory:
    factory = ProviderFactory()

    factory.register(
        ProviderType.MOCK,
        lambda config: MockProvider(config),
    )

    return factory


def test_provider_runtime_creates_llm_service():
    factory = build_factory()

    runtime = ProviderRuntime(
        factory,
        ProviderConfig(
            provider=ProviderType.MOCK,
            model="mock-model",
        ),
    )

    assert runtime.service is not None


def test_provider_runtime_exposes_provider_name():
    factory = build_factory()

    runtime = ProviderRuntime(
        factory,
        ProviderConfig(
            provider=ProviderType.MOCK,
            model="mock-model",
        ),
    )

    assert runtime.provider_name == "mock"


def test_provider_runtime_exposes_provider_type():
    factory = build_factory()

    runtime = ProviderRuntime(
        factory,
        ProviderConfig(
            provider=ProviderType.MOCK,
            model="mock-model",
        ),
    )

    assert runtime.provider_type == ProviderType.MOCK


def test_mock_runtime_factory():
    factory = build_factory()

    runtime = ProviderRuntime.mock(
        factory,
        model="test-model",
    )

    assert runtime.provider_type == ProviderType.MOCK
    assert runtime.service is not None
