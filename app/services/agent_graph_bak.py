
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
from app.services.graph.dependency_resolver import (
    resolve_execution_order
)
from app.services.graph.parallel_groups import (
    build_parallel_groups
)
from app.services.graph.parallel_executor import (
    execute_parallel
)
from app.services.graph.agent_runner import (
    run_agent
)
import time
import logging

logger = logging.getLogger(__name__)
timings = {}

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

    plan["execution_order"] = selected

    execution_order  = resolve_execution_order(
        selected,
        AGENT_REGISTRY
    )
    groups = build_parallel_groups(
        execution_order
    )

    state["selected_agents"] = selected
    
    state["execution"] = {
        "agents_executed": [],
        "agent_count": 0
    }

    state["execution"][
        "parallel_groups"
    ] = groups

    logger.info(f"ROUTE: {selected}")

    for agent_name in groups[0]:

        agent_info = AGENT_REGISTRY[
            agent_name
        ]

        agent = agent_info[
            "function"
        ]

        state = agent(state)

    start = time.perf_counter()

    state = agent(state)

    timings[agent_name] = round(
        time.perf_counter() - start,
        6
    )

    tasks = []

    for agent_name in groups[1]:

        agent_info = AGENT_REGISTRY[
            agent_name
        ]

        agent = agent_info[
            "function"
        ]

        tasks.append(
            (
                run_agent,
                (
                    agent,
                    state
                )
            )
        )

    results = execute_parallel(
        tasks
    )

    for result in results:

        if "actions" in result:
            state["actions"] = result[
                "actions"
            ]

        if "insights" in result:
            state["insights"] = result[
                "insights"
            ]

        if "findings" in result:
            state["findings"] = result[
                "findings"
            ]

    state["execution"][
        "parallel_groups"
    ] = groups
    state["execution"][
        "timings"
    ] = timings

    logger.info(f"AFTER ACTIONS: {state.get('actions')}")
    logger.info(f"AFTER INSIGHTS: {state.get('insights')}")
    logger.info(f"EXECUTION METADATA: {state.get('execution')}")
    print("EXECUTION:", state.get("execution"))
    print("EXECUTION ORDER:", state.get("plan", {}).get("execution_order"))
    print("REGISTERED:", AGENT_REGISTRY.keys())
    return state

"""
    for agent_name in selected:

        agent_info = AGENT_REGISTRY.get(
            agent_name
        )

        agent = agent_info["function"]

        if agent:

            state = agent(state)

            state["execution"]["agents_executed"].append(agent_name)

    state["execution"]["agent_count"] = len(state["execution"]["agents_executed"])
"""