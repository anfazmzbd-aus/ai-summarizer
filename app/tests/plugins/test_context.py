from app.plugins import PluginContext


def test_context():

    context = PluginContext()

    assert context.services == {}
    assert context.configuration == {}
