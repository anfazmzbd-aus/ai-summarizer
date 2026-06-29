class RetryEngine:

    def retry(

        self,

        fn,

        retries=1,

    ):

        last = None

        for _ in range(
            retries + 1
        ):

            try:

                return fn()

            except Exception as e:

                last = e

        raise last