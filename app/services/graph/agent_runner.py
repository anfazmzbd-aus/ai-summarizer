import time


def run_agent(agent_name, agent_func, state):

    local_state = state.copy()

    start = time.perf_counter()

    result = agent_func(local_state)

    duration = round(
        time.perf_counter() - start,
        6
    )

    return {
        "agent": agent_name,
        "duration": duration,
        "actions": result.get("actions", []),
        "insights": result.get("insights", []),
        "findings": result.get("findings", []),
        "trends": result.get("trends", [])
    }