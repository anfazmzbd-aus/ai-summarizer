# ADR-001

Title:
Replace Orchestration Runtime with Graph Execution Runtime

Status:
Accepted

Date:
2026-06-29

Decision:

Adopt ExecutionGraph as runtime contract.

Context:

V7.6 execution ordering caused coupling and retry complexity.

Consequences:

Positive:

* deterministic runtime
* isolated retries
* state contracts

Negative:

* migration complexity
* stricter schemas

Alternatives Considered:

Keep V7.6 runtime:
Rejected
