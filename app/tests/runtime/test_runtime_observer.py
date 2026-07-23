from app.runtime.observer.observer_context import (
    ObserverContext,
)

from app.runtime.observer.runtime_observer import (
    RuntimeObserver,
)


def make_observer():

    context = ObserverContext(
        execution_id="exec-1",
    )

    return RuntimeObserver(
        context,
    )


def test_execution_events():

    observer = make_observer()

    observer.execution_started()
    observer.execution_finished()

    assert observer.context.observations == [
        "execution_started",
        "execution_finished",
    ]


def test_layer_events():

    observer = make_observer()

    observer.layer_started(0)
    observer.layer_finished(0)

    assert observer.context.current_layer == 0

    assert observer.context.observations == [
        "layer_started:0",
        "layer_finished:0",
    ]


def test_node_events():

    observer = make_observer()

    observer.node_started("summary")
    observer.node_finished("summary")

    assert observer.context.current_node == "summary"

    assert observer.context.observations == [
        "node_started:summary",
        "node_finished:summary",
    ]


def test_event_order():

    observer = make_observer()

    observer.execution_started()

    observer.layer_started(0)

    observer.node_started("summary")

    observer.node_finished("summary")

    observer.layer_finished(0)

    observer.execution_finished()

    assert observer.context.observations == [
        "execution_started",
        "layer_started:0",
        "node_started:summary",
        "node_finished:summary",
        "layer_finished:0",
        "execution_finished",
    ]
