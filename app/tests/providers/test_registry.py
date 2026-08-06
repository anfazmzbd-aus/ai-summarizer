from app.providers.base import BaseProvider
from app.providers.health import ProviderHealth
from app.providers.models import (
    LLMRequest,
    LLMResponse,
)
from app.providers.registry import ProviderRegistry


class DummyProvider(BaseProvider):

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
        return ("dummy",)


def test_register_and_get():

    registry = ProviderRegistry()

    provider = DummyProvider()

    registry.register(
        "dummy",
        provider,
    )

    assert registry.get("dummy") is provider


def test_exists():

    registry = ProviderRegistry()

    registry.register(
        "dummy",
        DummyProvider(),
    )

    assert registry.exists("dummy") is True
    assert registry.exists("missing") is False


def test_unregister():

    registry = ProviderRegistry()

    registry.register(
        "dummy",
        DummyProvider(),
    )

    registry.unregister("dummy")

    assert registry.exists("dummy") is False


def test_duplicate_registration():

    registry = ProviderRegistry()

    registry.register(
        "dummy",
        DummyProvider(),
    )

    try:
        registry.register(
            "dummy",
            DummyProvider(),
        )
    except ValueError:
        assert True
    else:
        assert False


def test_provider_listing():

    registry = ProviderRegistry()

    registry.register(
        "dummy",
        DummyProvider(),
    )

    assert registry.list_providers() == ("dummy",)
