from app.services.logging.logger import logger


def build_parallel_groups(
    execution_order,
    registry
):

    # ONLY include agents that exist in registry
    execution_order = [
        a for a in execution_order
        if a in registry
    ]

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

            agent_info = registry.get(
                agent,
                {}
            )

            dependencies = (
                agent_info.get(
                    "depends_on",
                    []
                )
            )

            # SAFE: ignore unknown dependencies
            dependencies = [
                d for d in dependencies
                if d in registry
            ]

            if all(
                dep in completed
                for dep in dependencies
            ):

                current_group.append(
                    agent
                )

        if not current_group:

            raise Exception(
                f"Circular or invalid dependency graph: {remaining}"
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
        f"****PARALLEL GROUPS (parallel groups): "
        f"{groups}"
    )

    return groups