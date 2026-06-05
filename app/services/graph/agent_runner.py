import time
import copy
import logging
from app.services.logging.logger import logger

logger = logging.getLogger("agent_system")

def run_agent(agent_name, agent_func, state):
    logger.info(
        f"RUNNING AGENT: "
        f"{agent_name}"
    )
    
    local_state = copy.deepcopy(state)

    start = time.perf_counter()

    result = agent_func(local_state)

    duration = round(
        time.perf_counter() - start,
        6
    )

    logger.info(
        f"COMPLETED AGENT: "
        f"{agent_name} "
        f"in {duration}s"
    )
    logger.info(
        f"ARTIFACTS: "
        f"{state.get('artifacts', {})}"
    )

    return {
        "agent": agent_name,
        "duration": duration,
        "artifacts": result.get(
            "artifacts",
            {}
        )
    }