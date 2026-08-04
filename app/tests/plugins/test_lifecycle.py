from app.plugins import (
    AgentCapability,
    AgentPlugin,
    PluginContext,
    PluginLifecycle,
    PluginMetadata,
    PluginState,
)


class DemoPlugin(AgentPlugin):

    @property
    def metadata(self):
        return PluginMetadata(
            "demo",
            "1.0",
        )

    @property
    def capability(self):
        return AgentCapability(
            "summary",
            "1.0",
        )

    def create_agent(self):
        return object()

    def initialize(self, context: PluginContext):
        self.started = True

    def shutdown(self):
        self.started = False


def test_lifecycle():

    plugin = DemoPlugin()

    lifecycle = PluginLifecycle(plugin)

    lifecycle.initialize(PluginContext())

    assert lifecycle.state is PluginState.INITIALIZED

    lifecycle.activate()

    assert lifecycle.state is PluginState.ACTIVE

    lifecycle.stop()

    assert lifecycle.state is PluginState.STOPPED
