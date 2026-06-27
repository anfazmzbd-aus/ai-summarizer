import time
import uuid
from app.services.classifiers.intent_classifier import classify_intent
from app.services.strategies.strategy_builder import build_strategy
from app.services.routers.semantic_router import semantic_router
from app.services.registry.agent_registry import AGENT_REGISTRY
from app.services.graph.parallel_executor import execute_parallel, stabilize_parallel_order
from app.services.graph.agent_runner import run_agent
from app.services.logging.logger import logger
from app.services.graph.scheduler import Scheduler
from app.services.runtime.context_builder import build_execution_context
from app.services.logging.trace_logger import trace_logger
from app.services.runtime.executor import DAGExecutor

def run_graph(state):

    state["execution_id"] = (
        str(
            uuid.uuid4()
        )
    )

    graph_start = time.perf_counter()

    execution = (
        build_execution_context(
            state
        )
    )

    logger.info(f"****context_bulder->agent_graph: {execution}")

    state.update(
        execution
    )

    logger.info(f"****agent_graph immediately after: {state}")

    # --------------------------------------------------
    # Intent Classification
    # --------------------------------------------------

    intent_info = classify_intent(
        state["text"]
    )
    logger.info(f"****agent_graph intent_info : {intent_info}")
    # --------------------------------------------------
    # Strategy Builder
    # --------------------------------------------------

    strategy = build_strategy(
        intent_info["intents"]
    )

    logger.info(
        f"****agent_graph STRATEGY : "
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

        # only DAG groups
        "parallel_groups": [
            g
            for g in groups
            if "summary" not in g
        ],

        "timings": {},
        "trace_count": 0,

        # NEW
        "execution_events": [],

        "retry_count": 0,
        "failed_agents": []
    }

    #execution_metadata["traces"] = trace_logger.get_traces()
    timings = {}
    
    # --------------------------------------------------
    # Group 1
    # Usually Summary
    # --------------------------------------------------
    
    PREPROCESSING_NODE = "summary"

    if (PREPROCESSING_NODE in plan["selected_agents"]):

        agent_info = (
            AGENT_REGISTRY[
                PREPROCESSING_NODE
            ]
        )

        agent = (
            agent_info[
                "function"
            ]
        )

        logger.info(
            "****PREPROCESS START: summary"
        )

        start = time.perf_counter()

        state = agent(
            state
        )

        duration = round(
            time.perf_counter()
            - start,
            6
        )

        timings[
            PREPROCESSING_NODE
        ] = duration

        execution_metadata[
            "preprocessing"
        ] = {
            "agent": PREPROCESSING_NODE,
            "duration": duration,
            "output_size": len(
                state.get(
                    "summary",
                    ""
                )
            )
        }

        logger.info(
            f"****PREPROCESS END: {duration}s"
        )

    # --------------------------------------------------
    # Group 2+
    # Parallel
    # --------------------------------------------------
    failed = []
    results = []
    for group_index in range(1,
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

        executor = DAGExecutor()

        state, failed, results = (
            executor.execute_group(
                tasks,
                state
            )
        )

        failed = (
            failed
            or []
        )

        results = (
            results
            or []
        )

        if failed:

            state = executor.retry_failed(
                tasks,
                state,
                failed
            )

        # ensure retry results are counted
        for agent in failed:
            execution_metadata["agents_executed"].append(agent)

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
            execution_metadata[
                "execution_events"
            ].append(
                {
                    "agent": agent_name,
                    "stage": "dag",
                    "status": (
                        "failed"
                        if result.get("error")
                        else "success"
                    )
                }
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

    traces = (
        trace_logger.get_traces()
    )

    logger.debug(
        f"****TRACE SAMPLE: "
        f"{traces[-1] if traces else None}"
    )

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
    ] = (
        len(
            execution_metadata[
                "agents_executed"
            ]
        )
        +
        (
            1
            if "summary" in plan["selected_agents"]
            else 0
        )
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

    # --------------------------------------------------
    # trace_count logic
    # --------------------------------------------------

    execution_metadata[
        "trace_count"
    ] = len(
        traces
    )

    traces = (
        trace_logger.get_traces()
    )

    execution_metadata[
        "trace_count"
    ] = len(
        traces
    )

    execution_metadata[
        "trace_sample"
    ] = (
        traces[-1]
        if traces
        else None
    )

    execution_metadata[
        "retry_count"
    ] = len(
        failed
    )

    execution_metadata[
        "failed_agents"
    ] = failed
    logger.info(f"****TRACE COUNT: {len(traces)}")
    logger.info(f"****TRACE COUNT METADATA: {execution_metadata['trace_count']}")

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

    from app.services.runtime.runtime_snapshot import RuntimeSnapshot

    from app.services.runtime.metrics import RuntimeMetrics

    from app.services.runtime.graph_export import GraphExporter

    from app.routes.runtime import runtime_cache

    state[
        "snapshot"
    ] = (
        RuntimeSnapshot.create(
            state
        )
    )

    state[
        "metrics"
    ] = (
        RuntimeMetrics.collect(
            state
        )
    )

    state[
        "graph"
    ] = (
        GraphExporter.export(
            state
        )
    )

    runtime_cache.clear()

    runtime_cache.update(
        state[
            "metrics"
        ]
    )

    return state

