from app.runtime.cancellation_token import CancellationToken


def test_default_state() -> None:
    token = CancellationToken()

    assert token.cancelled is False
    assert token.is_cancelled() is False


def test_cancel() -> None:
    token = CancellationToken()

    token.cancel()

    assert token.cancelled is True
    assert token.is_cancelled() is True
