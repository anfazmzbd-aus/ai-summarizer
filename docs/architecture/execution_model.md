# V7.6 Execution Model

## Pipeline

Input
↓
Intent Classification
↓
Strategy Builder
↓
Section Parser
↓
Summary Preprocessing
↓
Scheduler
↓
DAG Validation
↓
Parallel Execution
↓
Retry Layer
↓
Aggregation
↓
Response

---

## Stage 1 — Preprocessing

Nodes:

* summary

Properties:

* runs once
* sequential
* excluded from DAG
* writes artifacts only

---

## Stage 2 — DAG Execution

Layer 1:
actions
insights
findings
sentiment

Layer 2:
trend
risk

Layer 3:
root_cause
forecast

Layer 4:
recommendation

Properties:

* dependency-driven
* parallel-safe
* immutable state merge

---

## Retry Rules

Retries execute from:
deepcopy(base_state)

Retry outputs:
merge_state()

No mutation of successful outputs.
