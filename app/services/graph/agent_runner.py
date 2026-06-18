import time
import copy
import uuid
from app.services.logging.logger import logger
from app.services.logging.trace_logger import trace_logger

logger.info("****agent_system")

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

    execution_id = (
        state[
            "execution_id"
        ]
    )

    trace = (
        trace_logger.start(
            execution_id,
            agent_name,
            {
                "context":
                    local_state.get(
                        "context",
                        {}
                    ),

                "selected_agents":
                    local_state.get(
                        "selected_agents",
                        []
                    )
            }
        )
    )

    start = time.perf_counter()

    try:

        result = (
            agent_func(
                local_state
            )
        )

        duration = round(
            time.perf_counter()
            - start,
            6
        )

        trace_logger.end(
            trace,
            {
                "artifacts":
                    result.get(
                        "artifacts",
                        {}
                    )
            },
            status="success"
        )

    except Exception as e:

        duration = round(
            time.perf_counter()
            - start,
            6
        )

        trace_logger.end(
            trace,
            {
                "error":
                    str(e)
            },
            status="failed"
        )

        raise

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

