from app.ai import RetryPolicy


def test_retry():

    policy = RetryPolicy()

    assert policy.max_attempts == 3
