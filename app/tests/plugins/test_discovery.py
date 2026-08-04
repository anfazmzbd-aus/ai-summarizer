from app.plugins import PluginDiscovery


def test_discovery(tmp_path):

    plugin_file = tmp_path / "demo.py"

    plugin_file.write_text(
        """
from app.plugins import Plugin, PluginMetadata


class Demo(Plugin):

    @property
    def metadata(self):
        return PluginMetadata(
            "demo",
            "1.0"
        )

    def initialize(self, context):
        pass

    def shutdown(self):
        pass


PLUGIN_CLASS = Demo
"""
    )

    discovery = PluginDiscovery(str(tmp_path))

    plugins = discovery.discover()

    assert len(plugins) == 1

    assert plugins[0].metadata.name == "demo"
