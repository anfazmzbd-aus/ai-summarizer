# ADR-0003: Runtime Lifecycle

**Status:** Accepted

**Context:** 
Previously, preprocessing steps (like the `summary` generation and `plan` orchestration) were mixed together with analytical agents inside the execution graph [26]. This contamination caused trace count mismatches (traces tracking only DAG nodes vs execution metadata tracking all agents), confused the graph validation layer, and created fake dependencies [26, 27]. 

**Decision:** 
We enforced a **Hard Boundary** that separates the lifecycle into two strict phases: **Preprocessing (Non-DAG)** and the **DAG Engine** [28-30]. Preprocessing nodes (like `summary`, `section_parser`, and `semantic_router`) run first to construct the `execution_plan` [28, 29]. The DAG Engine *only* accepts and schedules analytical agents (e.g., `insights`, `findings`, `sentiment`) [28, 30]. 

**Alternatives Considered:**
*   **Include Preprocessing in DAG:** Attempted originally, but rejected because preprocessing nodes do not share the same dependency constraints or retry semantics as analytical AI agents [26, 31].

**Consequences:** 
*   **Positive:** Achieves clean separation of concerns, guarantees that the DAG validation layer accurately enforces dependencies, and ensures observability metrics (like `trace_count`) align perfectly with execution metadata [32, 33].
*   **Negative:** Requires strict developer discipline to ensure no preprocessing functions are ever accidentally registered as executable DAG nodes [34].