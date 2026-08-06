from app.providers.base import BaseProvider
from app.providers.config import (
    ProviderConfig,
    ProviderType,
)
from app.providers.exceptions import ProviderError
from app.providers.factory import ProviderFactory
from app.providers.health import ProviderHealth
from app.providers.models import (
    LLMRequest,
    LLMResponse,
)


class DummyProvider(BaseProvider):

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        self.config = config

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def supports_streaming(self) -> bool:
        return False

    def chat(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        raise NotImplementedError

    def health_check(self) -> ProviderHealth:
        return ProviderHealth.healthy(
            provider=self.name,
            latency_ms=1,
        )

    def available_models(self) -> tuple[str, ...]:
        return ("dummy-model",)


def test_factory_creates_provider():

    factory = ProviderFactory()

    factory.register(
        ProviderType.MOCK,
        DummyProvider,
    )

    config = ProviderConfig(
        provider=ProviderType.MOCK,
        model="dummy-model",
    )

    provider = factory.create(config)

    assert isinstance(
        provider,
        DummyProvider,
    )

    assert provider.config == config


def test_factory_supported_providers():

    factory = ProviderFactory()

    factory.register(
        ProviderType.MOCK,
        DummyProvider,
    )

    assert factory.supported_providers() == (ProviderType.MOCK,)


def test_factory_unknown_provider():

    factory = ProviderFactory()

    config = ProviderConfig(
        provider=ProviderType.OPENAI,
        model="gpt-5",
    )

    try:
        factory.create(config)

    except ProviderError:
        assert True

    else:
        assert False


def test_duplicate_creator_registration():

    factory = ProviderFactory()

    factory.register(
        ProviderType.MOCK,
        DummyProvider,
    )

    try:
        factory.register(
            ProviderType.MOCK,
            DummyProvider,
        )

    except ValueError:
        assert True

    else:
        assert False


def test_factory_creator_override():

    factory = ProviderFactory()

    factory.register(
        ProviderType.MOCK,
        DummyProvider,
    )

    factory.register(
        ProviderType.MOCK,
        DummyProvider,
        overwrite=True,
    )

    assert factory.supported_providers() == (ProviderType.MOCK,)
