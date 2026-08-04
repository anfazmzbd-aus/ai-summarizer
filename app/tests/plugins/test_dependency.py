from app.plugins import PluginDependency


def test_dependency():

    dep = PluginDependency(
        "core",
        "8.0",
    )

    assert dep.name == "core"
