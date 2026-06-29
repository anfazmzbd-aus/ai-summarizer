# Migration — V7.6 → V7.7

## Objective

Replace orchestration execution with deterministic graph runtime.

---

## Mapping

V7.6 → V7.7

scheduler
→ graph_builder

execution_order
→ ExecutionGraph.layers

run_graph
→ execution_engine

shared_state
→ State

retry_graph
→ retry_engine

---

## Rules

Do:

* preserve contracts
* preserve business logic

Do Not:

* copy runtime code
* preserve ordering assumptions
* recreate mutable execution

---

## Repository Strategy

main
release/v7.6
develop
feature/v7.7-runtime
