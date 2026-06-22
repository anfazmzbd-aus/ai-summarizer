from app.services.logging.logger import logger


class RetryPolicy:

    def __init__(self, max_retries=2):
        self.max_retries = max_retries

    def should_retry(self, agent_name, attempt, error=None):

        if attempt >= self.max_retries:
            logger.info(
                f"****RETRY STOPPED: {agent_name}"
            )
            return False

        if agent_name in [
            "summary",
            "semantic_router",
            "section_parser"
        ]:
            return False

        logger.info(
            f"****RETRY ALLOWED: {agent_name} "
            f"(attempt {attempt})"
        )

        return True