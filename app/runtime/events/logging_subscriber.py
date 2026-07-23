class LoggingSubscriber:

    def __init__(self, logger):

        self.logger = logger

    def __call__(self, event):

        self.logger.info(
            "%s",
            event,
        )
