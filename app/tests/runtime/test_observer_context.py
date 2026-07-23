from app.runtime.observer.observer_context import (
    ObserverContext,
)


def test_record_observation():

    context = ObserverContext(
        execution_id="exec-1",
    )

    context.record(
        "execution_started",
    )

    assert context.observations == [
        "execution_started",
    ]


def test_current_layer():

    context = ObserverContext(
        execution_id="exec-1",
    )

    context.current_layer = 2

    assert context.current_layer == 2


def test_current_node():

    context = ObserverContext(
        execution_id="exec-1",
    )

    context.current_node = "summary"

    assert context.current_node == "summary"
