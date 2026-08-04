from app.plugins import (
    AgentCapability,
    AgentPlugin,
    PluginContext,
    PluginMetadata,
    PluginValidator,
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
        pass

    def shutdown(self):
        pass


def test_validator():

    validator = PluginValidator("8.0")

    assert validator.validate(
        DemoPlugin(),
        "7.9",
    )
