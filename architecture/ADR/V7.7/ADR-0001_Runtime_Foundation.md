# ADR-0001: Runtime Foundation

**Status:** Accepted

**Context:** 
Early versions of the system (V5 and V6) relied on a mutable, dict-based state and implicit sequential execution lists to run agents [1-3]. As the system scaled to include more agents (Summary, Actions, Insights, Findings, Risk, etc.), this procedural approach caused `KeyError` crashes, missing artifacts, and fragile execution flow [1, 2, 4]. We needed a production-grade, highly reliable foundation capable of deterministic routing and execution [3, 5].

**Decision:** 
We established a strict **Graph-Based Execution Engine (V7.7)** that treats the orchestration pipeline as a deterministic Directed Acyclic Graph (DAG) [5]. The system replaces list-based `execution_order` and `parallel_groups` with a typed `ExecutionGraph` object [6]. The architecture strictly separates concerns: a `graph_builder` constructs the DAG, a `graph_validator` verifies structural correctness, and an `execution_engine` runs it [7-9].

**Alternatives Considered:**
*   **Sequential Python Functions:** Kept the original hardcoded flow, but rejected due to inability to support complex conditional routing and parallel capabilities.
*   **Third-Party Orchestration Frameworks (e.g., LangGraph):** Acknowledged as an option, but we chose to build a custom DAG engine to maintain strict control over dependencies, latency, and custom execution logging before eventually migrating to an external framework [10].

**Consequences:** 
*   **Positive:** Completely eliminates entire classes of bugs (like `UnboundLocalError` and empty execution order crashes) [4]. It ensures deterministic replayability and establishes a highly scalable enterprise AI runtime [5, 11].
*   **Negative:** Increases architectural complexity and requires strict adherence to schema definitions (`graph_schema.py`) to build execution maps [12, 13].