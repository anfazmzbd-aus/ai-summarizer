import time

from app.services.classifiers.intent_classifier import (
    classify_intent
)

from app.services.strategies.strategy_builder import (
    build_strategy
)

from app.services.routers.semantic_router import (
    semantic_router
)

from app.services.registry.agent_registry import (
    AGENT_REGISTRY
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
import logging

logger = logging.getLogger(__name__)

def run_graph(state):
    graph_start = time.perf_counter()
    # --------------------------------------------------
    # Intent Classification
    # --------------------------------------------------

    intent_info = classify_intent(
        state["text"]
    )

    # --------------------------------------------------
    # Strategy Builder
    # --------------------------------------------------

    strategy = build_strategy(
        intent_info["intents"]
    )

    # --------------------------------------------------
    # Semantic Router
    # --------------------------------------------------

    plan = semantic_router(
        state["text"],
        intent_info,
        strategy
    )

    # --------------------------------------------------
    # Dependency Resolution
    # --------------------------------------------------

    execution_order = resolve_execution_order(
        plan["selected_agents"],
        AGENT_REGISTRY
    )

    plan["execution_order"] = (
        execution_order
    )

    # --------------------------------------------------
    # Parallel Groups
    # --------------------------------------------------

    groups = build_parallel_groups(
        execution_order
    )

    # --------------------------------------------------
    # Execution Metadata
    # --------------------------------------------------

    execution_metadata = {
        "agents_executed": [],
        "agent_count": 0,
        "parallel_groups": groups,
        "timings": {}
    }

    timings = {}

    # --------------------------------------------------
    # Group 1
    # Usually Summary
    # --------------------------------------------------

    if len(groups) > 0:

        for agent_name in groups[0]:

            agent_info = (
                AGENT_REGISTRY[
                    agent_name
                ]
            )

            agent = (
                agent_info[
                    "function"
                ]
            )

            start = (
                time.perf_counter()
            )

            state = agent(state)

            timings[
                agent_name
            ] = round(
                time.perf_counter()
                - start,
                6
            )

            execution_metadata[
                "agents_executed"
            ].append(
                agent_name
            )

    # --------------------------------------------------
    # Group 2+
    # Parallel
    # --------------------------------------------------

    if len(groups) > 1:

        tasks = []

        parallel_agents = (
            groups[1]
        )

        for agent_name in parallel_agents:

            agent_info = (
                AGENT_REGISTRY[
                    agent_name
                ]
            )

            agent = (
                agent_info[
                    "function"
                ]
            )

            tasks.append(
                (
                    run_agent,
                    (
                        agent_name,
                        agent,
                        state
                    )
                )
            )

        results = execute_parallel(
            tasks
        )

        for index, result in enumerate(
            results
        ):

            agent_name = result["agent"]

            timings[agent_name] = result["duration"]

            execution_metadata[
                "agents_executed"
            ].append(
                agent_name
            )

            if result.get("actions"):
                state["actions"] = result["actions"]

            if result.get("insights"):
                state["insights"] = result["insights"]

            if result.get("findings"):
                state["findings"] = result["findings"]

    execution_metadata[
        "agent_count"
    ] = len(
        execution_metadata[
            "agents_executed"
        ]
    )

    execution_metadata[
        "timings"
    ] = timings
    
    execution_metadata["total_execution_time"] = round(
    time.perf_counter() - graph_start,
    6
)
    # --------------------------------------------------
    # Save Plan
    # --------------------------------------------------

    state["plan"] = plan

    state[
        "execution"
    ] = execution_metadata

    #logger.info(f"ROUTE: {selected}")
    logger.info(f"AFTER ACTIONS: {state.get('actions')}")
    logger.info(f"AFTER INSIGHTS: {state.get('insights')}")
    logger.info(f"EXECUTION METADATA: {state.get('execution')}")
    return state