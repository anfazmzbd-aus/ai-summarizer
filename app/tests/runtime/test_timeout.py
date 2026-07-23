from app.runtime.timeout import Timeout


def test_timeout_seconds():

    timeout = Timeout(
        seconds=30,
    )

    assert timeout.seconds == 30
