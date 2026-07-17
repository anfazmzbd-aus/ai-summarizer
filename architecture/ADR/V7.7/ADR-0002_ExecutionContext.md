# ADR-0002: ExecutionContext

**Status:** Accepted

**Context:** 
During the integration of the parallel execution engine, we discovered that passing a shared, mutable `state` object to multiple concurrently running agents caused severe data contamination [14, 15]. Nested artifacts were being injected improperly, and downstream agents could inadvertently read partial updates from other agents executing in the same parallel group [16, 17]. Furthermore, retrying failed agents with a mutated state caused ghost executions and corrupted artifacts [18].

**Decision:** 
We implemented strict **Runtime Isolation** using an `ExecutionContext` [14, 19]. Every agent node is now given an isolated, immutable snapshot (deep copy) of the state via a `ContextBuilder` [17, 20]. Agents are explicitly forbidden from mutating the global state directly; instead, they return isolated outputs which are then committed deterministically by a `StateMerger` only after the agent succeeds [9, 21, 22].

**Alternatives Considered:**
*   **Thread Locks on Global State:** Rejected because it would introduce bottlenecks and ruin the performance gains of parallel execution.
*   **Shallow Copying:** Rejected because nested dict objects (like existing artifacts) would still be shared and mutated by reference [23].

**Consequences:** 
*   **Positive:** Completely eliminates cross-agent artifact pollution, guarantees safe and deterministic retries (as they start from a clean state snapshot), and provides stable execution tracing [24, 25].
*   **Negative:** Adds slight memory and performance overhead due to executing deep copies of the state dictionary before each node runs.