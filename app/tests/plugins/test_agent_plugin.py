from app.plugins import (
    AgentCapability,
    AgentPlugin,
    # PluginContext,
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

    def initialize(self, context):

        pass

    def shutdown(self):

        pass


def test_agent_plugin():

    plugin = DemoAgentPlugin()

    assert plugin.capability.name == "demo"

    assert plugin.create_agent() == "agent-instance"
