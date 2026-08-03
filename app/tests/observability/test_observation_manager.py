from app.observability.context import (
    ObservationManager,
)


def test_manager():

    manager = ObservationManager()

    context = manager.create()

    manager.finish(context)

    assert context.observation.finished_at is not None
