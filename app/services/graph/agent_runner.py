import time
import copy
import logging
from app.services.logging.logger import logger

logger = logging.getLogger("agent_system")

def run_agent(agent_name, agent_func, state):
    logger.info(
        f"****RUNNING AGENT: "
        f"{agent_name}"
    )

    sections = state.get(
        "sections",
        {}
    )

    local_state = copy.deepcopy(state)

    local_state["active_section"] = (
        sections.get(
            state.get(
                "primary_intent"
            ),
            state["text"]
        )
    )

    start = time.perf_counter()

    result = agent_func(local_state)

    duration = round(
        time.perf_counter() - start,
        6
    )

    logger.info(
        f"****COMPLETED AGENT: "
        f"{agent_name} "
        f"in {duration}s"
    )

    logger.info(
        f"****AGENT CONTEXT SNAPSHOT: "
        f"{state.get('context', {})}"
    )
    artifacts = result.get(
    "artifacts",
    {}
    )
    logger.info(
        f"****ARTIFACTS: "
        f"{artifacts}"
    )

    return {
        "agent": agent_name,
        "duration": duration,
        "artifacts": artifacts
    }

