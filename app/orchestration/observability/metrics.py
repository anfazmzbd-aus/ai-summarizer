class RuntimeMetrics:

    def __init__(self):

        self.values = {}

    def increment(
        self,
        key,
        amount=1,
    ):

        self.values[key] = (
            self.values.get(
                key,
                0,
            )
            + amount
        )

    def observe(
        self,
        key,
        value,
    ):

        self.values[key] = value

    def export(self):

        return dict(self.values)
