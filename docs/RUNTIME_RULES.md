# Runtime Rules (V7.7+)

These rules are mandatory.

Violation requires architecture review.

---

## Rule 1 — ExecutionGraph Is Source of Truth

Allowed:

Scheduler
→ ExecutionGraph
→ ExecutionEngine

Forbidden:

Scheduler
→ execution_order
→ runtime

---

## Rule 2 — Runtime Never Builds Dependencies

Allowed:

graph_builder computes DAG

Forbidden:

execution_engine creates dependencies

---

## Rule 3 — State Is Immutable Between Nodes

Allowed:

state.node_outputs[node]

Forbidden:

shared state mutation

Forbidden:

state["summary"] = ...

---

## Rule 4 — Contracts Are Mandatory

Every node must declare:

INPUT
OUTPUT
RETRY

Execution without contract validation is invalid.

---

## Rule 5 — Retry Scope

Retry target:

single node

Forbidden:

rerun entire graph

---

## Rule 6 — Preprocessing Isolation

Preprocessing:

before graph

Forbidden:

summary preprocessing inside DAG

---

## Rule 7 — Runtime Cannot Mutate Graph

ExecutionGraph is immutable.

Forbidden:

graph.layers.append(...)
