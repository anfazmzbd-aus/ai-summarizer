from app.observability.dependencies import (
    get_observability,
)


def test_dependency_singleton():

    first = get_observability()

    second = get_observability()

    assert first is second
