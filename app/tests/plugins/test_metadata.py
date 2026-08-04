from app.plugins import PluginMetadata


def test_metadata():

    metadata = PluginMetadata(
        name="demo",
        version="1.0.0",
    )

    assert metadata.name == "demo"
    assert metadata.version == "1.0.0"
