import time
from app.services.classifiers.intent_classifier import classify_intent
from app.services.strategies.strategy_builder import build_strategy
from app.services.routers.semantic_router import semantic_router
from app.services.registry.agent_registry import AGENT_REGISTRY
#from app.services.graph.dependency_resolver import resolve_execution_order
#from app.services.graph.parallel_groups import build_parallel_groups
from app.services.graph.parallel_executor import execute_parallel, stabilize_parallel_order
from app.services.graph.agent_runner import run_agent
#import logging
from app.services.logging.logger import logger
#from app.services.graph.graph_validator import validate_execution_graph
from app.services.graph.scheduler import Scheduler

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

    logger.info(
        f"****STRATEGY: "
        f"{strategy}"
    )
    # --------------------------------------------------
    # Semantic Router
    # --------------------------------------------------

    plan = semantic_router(
        state["text"],
        intent_info,
        strategy
    )

    state["sections"] = (
        plan.get(
            "sections",
            {}
        )
    )

    state["context"] = {
        "insights": state["artifacts"].get("insights", []),
        "findings": state["artifacts"].get("findings", []),
        "actions": state["artifacts"].get("actions", []),
        "trends": state["artifacts"].get("trends", []),
        "risk": state["artifacts"].get("risk", []),
    }
    # -------------------------------------------------------------------------------
    # Dependency Resolution -> moved to app/services/graph/scheduler.py in V7.6 ph1
    # -------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------
    # Parallel Groups -> moved to app/services/graph/scheduler.py in V7.6 ph1
    # -------------------------------------------------------------------------------

    execution_plan = (
        Scheduler.build_execution_plan(
            plan["selected_agents"],
            AGENT_REGISTRY
        )
    )

    plan["selected_agents"] = (
        execution_plan[
            "selected_agents"
        ]
    )

    plan["execution_order"] = (
        execution_plan[
            "execution_order"
        ]
    )

    plan["parallel_groups"] = (
        execution_plan[
            "parallel_groups"
        ]
    )

    plan.setdefault(
        "metadata",
        {}
    )

    plan["metadata"].update(
        execution_plan[
            "metadata"
        ]
    )

    groups = (
        plan[
            "parallel_groups"
        ]
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

    for group_index in range(
        1,
        len(groups)
    ):

        tasks = []

        parallel_agents = (
            groups[group_index]
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
        #results = reorder_results(results, execution_order)
        agent_order_map = {
            agent: i
            for i, agent in enumerate(
                groups[group_index]
            )
        }

        results = sorted(
            results,
            key=lambda r: agent_order_map.get(
                r["agent"],
                999
            )
        )
        results = stabilize_parallel_order(
            results,
            groups[group_index]
        )
        logger.info(
            f"****GROUP {group_index} RESULTS"
            f"{results}"
        )

        for result in results:

            agent_name = result["agent"]

            timings[
                agent_name
            ] = result["duration"]

            execution_metadata[
                "agents_executed"
            ].append(
                agent_name
            )

            artifacts = result.get(
                "artifacts",
                {}
            )

            for key, value in artifacts.items():

                state.setdefault(
                    "artifacts",
                    {}
                )[key] = value

    state["context"] = {

        "insights":
            state["artifacts"].get(
                "insights",
                []
            ),

        "findings":
            state["artifacts"].get(
                "findings",
                []
            ),

        "actions":
            state["artifacts"].get(
                "actions",
                []
            ),

        "trends":
            state["artifacts"].get(
                "trends",
                []
            ),

        "risk":
            state["artifacts"].get(
                "risk",
                []
            )
    }

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
    
    execution_metadata[
        "total_execution_time"
    ] = round(
        time.perf_counter()
        - graph_start,
        6
    )
    # --------------------------------------------------
    # Save Plan
    # --------------------------------------------------

    state["plan"] = plan

    state[
        "execution"
    ] = execution_metadata

    # --------------------------------------------------
    # Debug prints
    # --------------------------------------------------
    logger.debug(f"****ROUTE: {plan['selected_agents']}")
    logger.debug(f"****AFTER ACTIONS: {state.get('actions')}")
    logger.debug(f"****AFTER INSIGHTS: {state.get('insights')}")
    logger.debug(f"****AFTER TRENDS: {state.get('trends')}")
    logger.debug("=== DEBUG: AGENT GRAPH EXECUTION START===")
    logger.debug(f"MERGED ARTIFACTS: {state['artifacts']}")
    logger.debug(f"REGISTERED: {AGENT_REGISTRY.keys()}")
    logger.debug(f"EXECUTED AGENTS: {execution_metadata['agents_executed']}")
    logger.info(f"****EXECUTION METADATA: {state.get('execution')}")
    logger.debug(f"ARTIFACTS: {state.get('artifacts', {})}")
    logger.debug("=== DEBUG: AGENT GRAPH EXECUTION END===")

    return state

