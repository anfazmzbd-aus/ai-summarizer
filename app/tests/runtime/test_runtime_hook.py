import pytest

from app.runtime.hooks.runtime_hook import RuntimeHook


class DummyHook(RuntimeHook):

    def before_node(
        self,
        context,
        node,
    ):
        self.before_node_called = True

    def after_node(
        self,
        context,
        node,
        result,
    ):
        self.after_node_called = True

    def before_layer(
        self,
        context,
        layer,
    ):
        self.before_layer_called = True

    def after_layer(
        self,
        context,
        layer,
    ):
        self.after_layer_called = True


def test_runtime_hook_is_abstract():

    with pytest.raises(TypeError):
        RuntimeHook()


def test_runtime_hook_implementation():

    hook = DummyHook()

    hook.before_node(None, "summary")
    hook.after_node(None, "summary", {})
    hook.before_layer(None, 0)
    hook.after_layer(None, 0)

    assert hook.before_node_called
    assert hook.after_node_called
    assert hook.before_layer_called
    assert hook.after_layer_called
