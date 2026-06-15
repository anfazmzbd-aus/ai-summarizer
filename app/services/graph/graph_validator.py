from app.services.logging.logger import logger


def validate_execution_graph(
    execution_order,
    AGENT_REGISTRY
):

    errors = []
    warnings = []

    registry_keys = set(AGENT_REGISTRY.keys())
    execution_set = set(execution_order)

    # 1. Unknown agents in execution order
    unknown_agents = execution_set - registry_keys

    if unknown_agents:
        errors.append(
            f"Unknown agents in execution_order: {unknown_agents}"
        )

    # 2. Unused registry agents (optional warning)
    unused_agents = registry_keys - execution_set

    ignored = {
        "plan",
        "actions"
    }

    unused_agents -= ignored

    if unused_agents:
        warnings.append(
            f"Unused registry agents: {unused_agents}"
        )

    # 3. Dependency validation
    for agent in execution_order:

        agent_info = AGENT_REGISTRY.get(agent, {})

        dependencies = agent_info.get("depends_on", [])

        missing_deps = [
            d for d in dependencies
            if d not in execution_set
        ]

        if missing_deps:
            errors.append(
                f"{agent} missing dependencies: {missing_deps}"
            )

    if errors:

        logger.error("GRAPH VALIDATION FAILED")

        for e in errors:
            logger.error(e)

        raise Exception("Invalid execution graph")

    logger.info(
        f"****GRAPH VALIDATION PASSED | warnings={warnings}"
    )

    return True