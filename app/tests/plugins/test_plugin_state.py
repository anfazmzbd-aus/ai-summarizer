from app.plugins import PluginState


def test_state():

    assert PluginState.ACTIVE.value == "active"
