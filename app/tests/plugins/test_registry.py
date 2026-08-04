from app.plugins import (
    Plugin,
    PluginMetadata,
    PluginRegistry,
)


class DemoPlugin(Plugin):

    @property
    def metadata(self):

        return PluginMetadata(
            "demo",
            "1.0",
        )

    def initialize(self, context):
        pass

    def shutdown(self):
        pass


def test_registry():

    registry = PluginRegistry()

    registry.add(DemoPlugin())

    assert registry.count() == 1

    assert registry.get("demo") is not None
