from .router import router_node
from .agents import (
    summary_agent,
    actions_agent,
    insights_agent,
    findings_agent,
    plan_agent
)
from app.services.registry.agent_registry import (
    AGENT_REGISTRY
)
from app.services.routers.semantic_router import (
    semantic_router
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

    plan = semantic_router(
        state["text"]
    )

    state["plan"] = plan

    selected = plan["selected_agents"]

    state["selected_agents"] = selected
    
    state["execution"] = {
        "agents_executed": selected
    }
    #state = plan_agent(state)

    #state["metadata"]["route"] = state["selected_agents"]

    #selected = state["selected_agents"]

    logger.info(f"ROUTE: {selected}")

    for agent_name in selected:

        agent = AGENT_REGISTRY.get(
            agent_name
        )

        if agent:
            state = agent(state)

    if "findings" in selected:
        state = findings_agent(state)

    logger.info(f"AFTER ACTIONS: {state.get('actions')}")
    logger.info(f"AFTER INSIGHTS: {state.get('insights')}")
    logger.info(f"AFTER FINDINGS: {state.get('findings')}")

    return state

