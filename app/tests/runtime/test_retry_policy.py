from app.runtime.retry_policy import RetryPolicy


def test_retry_policy_defaults() -> None:
    policy = RetryPolicy()

    assert policy.enabled is True
    assert policy.max_attempts == 3
    assert policy.delay_seconds == 0.0
    assert policy.exponential_backoff is False
    assert policy.retry_exceptions == (Exception,)
