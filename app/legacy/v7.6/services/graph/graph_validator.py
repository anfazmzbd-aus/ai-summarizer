from app.services.logging.logger import logger


def validate_execution_graph(
    execution_order,
    AGENT_REGISTRY
):
    NON_DAG_NODES = {"summary", "plan", "semantic_router", "section_parser"}
    errors = []
    warnings = []

    registry_keys = set(AGENT_REGISTRY.keys())
    execution_set = set(execution_order)

    # 0. Block preprocessing nodes in DAG
    illegal_nodes = execution_set.intersection(NON_DAG_NODES)

    if illegal_nodes:
        errors.append(
            f"Preprocessing nodes found in DAG execution_order: {illegal_nodes}"
        )

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

        if agent not in AGENT_REGISTRY:
            continue

        if agent in NON_DAG_NODES:
            continue  # already handled above

        dependencies = AGENT_REGISTRY[agent].get("depends_on", [])

        for dep in dependencies:
            if dep in NON_DAG_NODES:
                errors.append(
                    f"{agent} depends on non-DAG node: {dep}"
                )
                
        missing_deps = [
            d for d in dependencies
            if d not in execution_set
        ]

        if missing_deps:
            errors.append(
                f"{agent} missing dependencies: {missing_deps}"
            )

    if errors:

        logger.error(
            "****GRAPH VALIDATION FAILED"
        )

        for e in errors:

            logger.error(
                f"****GRAPH ERROR: {e}"
            )

        raise Exception(
            "\n".join(errors)
        )

    logger.info(
        f"****GRAPH VALIDATION PASSED | warnings={warnings}"
    )

    return True