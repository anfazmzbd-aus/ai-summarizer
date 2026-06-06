from app.services.logging.logger import logger

def resolve_execution_order(
    selected_agents,
    registry
):

    resolved = []
    visited = set()
    
    def get_dependencies(
        agent_name,
        registry
    ):
        return registry[
            agent_name
        ].get(
            "depends_on",
            []
        )

    def visit(agent_name):

        if agent_name in visited:
            return

        visited.add(agent_name)

        agent_info = registry.get(
            agent_name,
            {}
        )

        dependencies = agent_info.get(
            "depends_on",
            []
        )

        for dependency in dependencies:
            visit(dependency)

        resolved.append(agent_name)

    for agent in selected_agents:
        visit(agent)
    logger.info(f"Resolved execution order: {resolved}")
    return resolved