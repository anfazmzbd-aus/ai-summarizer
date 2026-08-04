from app.plugins import (
    AgentCapability,
    AgentPlugin,
    CapabilityDiscovery,
    PluginContext,
    PluginManager,
    PluginMetadata,
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
            "Demo capability",
        )

    def create_agent(self):
        return object()

    def initialize(self, context: PluginContext):
        pass

    def shutdown(self):
        pass


def test_discovery():

    manager = PluginManager()

    manager.register(DemoPlugin())

    registry = CapabilityDiscovery().discover(manager)

    assert registry.count() == 1

    capability = registry.get("summary")

    assert capability is not None
    assert capability.plugin == "demo"
    assert capability.description == "Demo capability"
