from app.observability.context import Observation


def test_finish():

    obs = Observation()

    assert obs.finished_at is None

    obs.finish()

    assert obs.finished_at is not None
