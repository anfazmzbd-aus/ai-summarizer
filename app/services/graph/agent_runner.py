import time
import copy


def run_agent(agent_name, agent_func, state):

    local_state = copy.deepcopy(state)

    start = time.perf_counter()

    result = agent_func(local_state)

    duration = round(
        time.perf_counter() - start,
        6
    )

    return {
        "agent": agent_name,
        "duration": duration,
        "artifacts": result.get(
            "artifacts",
            {}
        )
    }