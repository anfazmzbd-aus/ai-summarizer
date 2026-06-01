from .router import router_node
from .agents import (
    summary_agent,
    actions_agent,
    insights_agent,
    findings_agent,
    plan_agent
)
import logging
logger = logging.getLogger(__name__)

AGENTS = {
    "summary": summary_agent,
    "actions": actions_agent,
    "insights": insights_agent,
    "findings": findings_agent,
    "plan": plan_agent
}


def run_graph(state):

    state = plan_agent(state)

    state["metadata"]["route"] = state["selected_agents"]

    selected = state["selected_agents"]

    logger.info(f"ROUTE: {selected}")

    if "summary" in selected:
        state = summary_agent(state)

    if "actions" in selected:
        state = actions_agent(state)

    if "insights" in selected:
        state = insights_agent(state)

    if "findings" in selected:
        state = findings_agent(state)

    logger.info(f"AFTER ACTIONS: {state.get('actions')}")
    logger.info(f"AFTER INSIGHTS: {state.get('insights')}")
    logger.info(f"AFTER FINDINGS: {state.get('findings')}")

    return state

