from app.services.logging.logger import logger


def build_parallel_groups(
    execution_order,
    registry
):

    remaining = set(
        execution_order
    )

    completed = set()

    groups = []

    while remaining:

        current_group = []

        for agent in list(
            remaining
        ):

            dependencies = registry[
                agent
            ].get(
                "depends_on",
                []
            )

            if all(
                dep in completed
                for dep in dependencies
            ):

                current_group.append(
                    agent
                )

        if not current_group:

            raise Exception(
                "Circular dependency detected"
            )

        groups.append(
            current_group
        )

        completed.update(
            current_group
        )

        remaining -= set(
            current_group
        )

    logger.info(
        f"PARALLEL GROUPS: "
        f"{groups}"
    )

    return groups