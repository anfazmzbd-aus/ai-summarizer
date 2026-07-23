import pytest

from app.runtime.middleware import RuntimeMiddleware


class DummyMiddleware(RuntimeMiddleware):

    def __init__(self):
        self.before_called = False
        self.after_called = False

    def before_execution(
        self,
        runtime_context,
    ):
        self.before_called = True

    def after_execution(
        self,
        runtime_context,
        result,
    ):
        self.after_called = True


def test_before_execution_called():

    middleware = DummyMiddleware()

    middleware.before_execution(None)

    assert middleware.before_called


def test_after_execution_called():

    middleware = DummyMiddleware()

    middleware.after_execution(None, {})

    assert middleware.after_called


def test_runtime_middleware_is_abstract():

    with pytest.raises(TypeError):
        RuntimeMiddleware()
