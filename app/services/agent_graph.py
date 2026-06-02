
from app.services.registry.agent_registry import (
    AGENT_REGISTRY
)

from app.services.routers.semantic_router import (
    semantic_router
)

from app.services.classifiers.intent_classifier import (
    classify_intent
)

from app.services.strategies.strategy_builder import (
    build_strategy
)

import logging

logger = logging.getLogger(__name__)


def run_graph(state):

    intent_info = classify_intent(
        state["text"]
    )

    strategy = build_strategy(
        intent_info["intents"]
    )

    plan = semantic_router(
        state["text"],
        intent_info,
        strategy
    )

    state["plan"] = plan

    selected = plan["selected_agents"]

    state["selected_agents"] = selected

    state["execution"] = {
        "agents_executed": [],
        "agent_count": 0
    }

    logger.info(f"ROUTE: {selected}")

    for agent_name in selected:

        agent = AGENT_REGISTRY.get(agent_name)

        if agent:

            state = agent(state)

            state["execution"]["agents_executed"].append(agent_name)

    state["execution"]["agent_count"] = len(state["execution"]["agents_executed"])

    #if "findings" in selected:
       # state = findings_agent(state)

    logger.info(f"AFTER ACTIONS: {state.get('actions')}")
    logger.info(f"AFTER INSIGHTS: {state.get('insights')}")
    #logger.info(f"AFTER FINDINGS: {state.get('findings')}")
    logger.info(f"EXECUTION METADATA: {state.get('execution')}")
    print("EXECUTION:", state.get("execution"))
    print("REGISTERED:", AGENT_REGISTRY.keys())
    return state

