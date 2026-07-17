# ADR-0005: Parallel Execution Strategy

**Status:** Accepted

**Context:** 
Executing complex, multi-agent workflows sequentially (e.g., waiting for `insights` to finish before starting `findings` or `sentiment`) resulted in high latency, even though these agents had no overlapping dependencies [44]. 

**Decision:** 
We introduced a **Parallel Execution Engine** utilizing layered execution batches [45]. The scheduler groups topologically sorted, independent agents into discrete layers (e.g., Group 1: `[insights, findings, sentiment]`) [45]. All agents within the same group execute concurrently via a `ThreadPoolExecutor` [46]. The system then utilizes a `stabilize_parallel_order` step to deterministically sort the results before merging the state, preventing any non-deterministic timing drift [47].

**Alternatives Considered:**
*   **Full Asynchronous Execution (Un-layered):** Permitting agents to execute completely asynchronously as soon as their dependencies resolve. Rejected for V7.6 due to the extreme complexity of preventing race conditions during state merging. Layered batching was chosen as a safer, deterministic intermediate step [9].

**Consequences:** 
*   **Positive:** Maximizes performance by reducing execution latency substantially [48]. It guarantees that Layer N completes successfully before Layer N+1 begins, ensuring strict data availability for downstream nodes [9].
*   **Negative:** Slower agents within a specific parallel group bottleneck the entire layer, meaning the next layer cannot start until the slowest thread in the current batch completes.