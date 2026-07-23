from unittest.mock import Mock

from app.runtime.hooks.hook_manager import HookManager


def test_register_hook():

    manager = HookManager()

    hook = Mock()

    manager.register(hook)

    assert len(manager._hooks) == 1


def test_before_node():

    manager = HookManager()

    hook = Mock()

    manager.register(hook)

    manager.before_node(
        None,
        "summary",
    )

    hook.before_node.assert_called_once()


def test_after_node():

    manager = HookManager()

    hook = Mock()

    manager.register(hook)

    manager.after_node(
        None,
        "summary",
        {},
    )

    hook.after_node.assert_called_once()


def test_layer_hooks():

    manager = HookManager()

    hook = Mock()

    manager.register(hook)

    manager.before_layer(
        None,
        0,
    )

    manager.after_layer(
        None,
        0,
    )

    hook.before_layer.assert_called_once()
    hook.after_layer.assert_called_once()
