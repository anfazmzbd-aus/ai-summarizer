from app.services.logging.logger import logger

def resolve_execution_order(
    selected_agents,
    registry
):

    resolved = []
    visiting = set()
    visited = set()
    NON_DAG_NODES = {
        "summary",
        "plan",
        "semantic_router",
        "section_parser"
    }
    def visit(agent):

        if agent in visited:
            return

        if agent in visiting:
            raise Exception(
                f"Circular dependency detected at {agent}"
            )

        visiting.add(agent)

        deps = registry.get(
            agent,
            {}
        ).get(
            "depends_on",
            []
        )

        for dep in deps:
            if dep in NON_DAG_NODES:
                logger.debug(
                    f"Skipping preprocessing dependency: {dep}"
                )
                continue

            if dep not in registry:

                raise Exception(
                    f"Unknown dependency: {dep}"
                )

            visit(dep)

        visiting.remove(agent)
        visited.add(agent)
        resolved.append(agent)

    for agent in selected_agents:

        visit(agent)

    logger.info(
        f"****Resolved execution order: {resolved}"
    )

    return resolved

