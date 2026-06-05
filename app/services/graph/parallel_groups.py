from app.services.logging.logger import logger
def build_parallel_groups(
    execution_order
):

    if (
        "summary"
        in execution_order
    ):

        remaining = [
            a
            for a in execution_order
            if a != "summary"
        ]

        return [
            ["summary"],
            remaining
        ]

    logger.info(
        f"EXECUTION ORDER: "
        f"{execution_order}"
    )

    return [execution_order]