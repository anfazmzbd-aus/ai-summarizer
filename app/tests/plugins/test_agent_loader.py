from app.plugins import (
    AgentCapability,
    AgentPlugin,
    AgentPluginLoader,
    PluginContext,
    PluginMetadata,
)


class DemoAgentPlugin(AgentPlugin):

    @property
    def metadata(self):
        return PluginMetadata(
            "demo-agent",
            "1.0",
        )

    @property
    def capability(self):
        return AgentCapability(
            "demo",
            "1.0",
        )

    def create_agent(self):
        return "agent-instance"

    def initialize(self, context: PluginContext):
        pass

    def shutdown(self):
        pass


def test_agent_loader():

    loader = AgentPluginLoader()

    loader.register(DemoAgentPlugin())

    assert loader.count() == 1

    assert loader.get("demo") == "agent-instance"
