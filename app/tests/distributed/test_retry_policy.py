from app.distributed.recovery import RetryPolicy


def test_should_retry():

    policy = RetryPolicy(max_attempts=3)

    assert policy.should_retry(0)
    assert policy.should_retry(2)
    assert not policy.should_retry(3)


def test_backoff():

    policy = RetryPolicy(backoff_seconds=2)

    assert policy.next_delay(0) == 2
    assert policy.next_delay(1) == 4
    assert policy.next_delay(2) == 8
