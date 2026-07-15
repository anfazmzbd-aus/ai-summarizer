import logging

logger = logging.getLogger("runtime")


class TraceLogger:

    def info(
        self,
        message,
    ):

        logger.info(message)

    def error(
        self,
        message,
    ):

        logger.error(message)
