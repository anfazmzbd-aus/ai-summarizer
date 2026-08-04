from app.plugins import (
    Plugin,
    PluginContext,
    PluginManager,
    PluginMetadata,
)


class DemoPlugin(Plugin):

    @property
    def metadata(self):

        return PluginMetadata(
            "demo",
            "1.0.0",
        )

    def initialize(self, context):

        self.started = True

    def shutdown(self):

        self.started = False


def test_manager():

    manager = PluginManager()

    plugin = DemoPlugin()

    manager.register(plugin)

    manager.initialize_all(PluginContext())

    assert manager.count() == 1

    assert plugin.started

    manager.shutdown_all()

    assert not plugin.started
