from app.plugins import PluginLoader


def test_loader():

    loader = PluginLoader()

    plugin = loader.load("app.tests.plugins.sample_plugin")

    assert plugin.metadata.name == "sample"
