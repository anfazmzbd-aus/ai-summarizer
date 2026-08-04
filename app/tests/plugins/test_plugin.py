from app.plugins import (
    Plugin,
    PluginContext,
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


def test_plugin():

    plugin = DemoPlugin()

    plugin.initialize(PluginContext())

    assert plugin.started

    plugin.shutdown()

    assert not plugin.started
