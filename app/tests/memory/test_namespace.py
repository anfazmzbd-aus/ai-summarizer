from app.memory import MemoryNamespace


def test_namespace():

    assert MemoryNamespace.EXECUTION.value == "execution"
    assert MemoryNamespace.SESSION.value == "session"
