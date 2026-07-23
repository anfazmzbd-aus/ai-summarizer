class FakeAgent:

    def __init__(self, result):
        self.result = result

    def run(self, state):
        return self.result


class FailingAgent:

    def run(self, state):
        raise RuntimeError("failure")


class RetryAgent:

    def __init__(self):
        self.calls = 0

    def run(self, state):
        self.calls += 1

        if self.calls < 2:
            raise RuntimeError("retry")

        return {"status": "ok"}


class SlowAgent:

    def run(self, state):
        import time

        time.sleep(0.05)

        return {"slow": True}
