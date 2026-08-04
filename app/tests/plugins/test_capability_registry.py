from app.plugins import (
    CapabilityInfo,
    CapabilityRegistry,
)


def test_registry():

    registry = CapabilityRegistry()

    registry.register(
        CapabilityInfo(
            name="summary",
            version="1.0",
            plugin="demo",
        )
    )

    assert registry.count() == 1

    assert registry.get("summary") is not None
