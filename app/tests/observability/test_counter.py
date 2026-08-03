from app.observability.metrics import Counter


def test_counter():

    counter = Counter("tasks")

    counter.increment()

    counter.increment(4)

    assert counter.value == 5
