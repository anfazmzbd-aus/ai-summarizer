# ADR-0004: Dependency Rules

**Status:** Accepted

**Context:** 
Early execution sequences were hardcoded sequentially (e.g., `summary` -> `actions` -> `insights` -> `findings`) [35]. As new context-aware agents were added (like `forecast` depending on `trend`, and `recommendation` depending on `risk` and `forecast`), manual mapping became impossible to maintain [36-38]. It caused situations where agents failed because their required upstream data had not been generated yet.

**Decision:** 
We adopted a **Registry-Driven Dependency Enforcement** system [39]. Agents now dynamically declare their dependencies during registration (e.g., `@register_agent("recommendation", depends_on=["forecast", "risk"])`) [36]. A `dependency_resolver` uses topological sorting to dynamically build the `ExecutionGraph`, automatically injecting missing upstream dependencies required to execute the user's selected intents [8, 40, 41]. 

**Alternatives Considered:**
*   **Hardcoded Strategy Maps:** Relying solely on `strategy_builder.py` to define the exact list of executing agents [42]. Rejected because it violated the Single Source of Truth principle and resulted in brittle execution ordering [42].

**Consequences:** 
*   **Positive:** The graph can now build itself dynamically from the `AGENT_REGISTRY` [39]. Developers can drop in a new agent without touching execution orchestration [43].
*   **Negative:** Circular dependencies are now possible if poorly configured, requiring the implementation of a `graph_validator` with strict cycle detection to fail invalid DAGs before runtime [8].