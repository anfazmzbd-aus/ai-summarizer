from app.runtime.timeout import Timeout


class TimeoutExecutor:
    """
    Executes work under a timeout policy.

    V1 intentionally delegates directly.
    Future versions will enforce real timeouts.
    """

    def __init__(
        self,
        timeout: Timeout,
    ):
        self.timeout = timeout

    def run(
        self,
        func,
        *args,
        **kwargs,
    ):
        return func(
            *args,
            **kwargs,
        )
