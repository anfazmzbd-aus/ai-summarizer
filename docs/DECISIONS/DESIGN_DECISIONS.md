## V7.7-stable

Record why you changed from V6 to V7.

Topics

Why DAG
Why immutable graph
Why Scheduler
Why GraphBuilder
Why LayerExecutor
Why NodeExecutor
Why ContractManager
Why ResponseBuilder

Future contributors will understand the architecture immediately.

V7.7 Execution Engine — Graph-Based Runtime

Below is the formalized V7.7 architecture specification with strict separation between **graph construction**, **graph validation**, and **graph execution**, enforcing deterministic semantics and contract-driven state isolation.

---

# V7.7 Execution Engine — Graph-Based Runtime Specification

## 1. Core System Definition

V7.7 defines the system as a:

> **Deterministic Directed Acyclic Graph (DAG) execution runtime with strict state contracts and node isolation guarantees**

All prior concepts of:

* execution_order
* parallel_groups
* mutable shared runtime state
  are removed from semantic responsibility and replaced with graph-first execution semantics.

---

# 2. Primary Data Structure

## 2.1 ExecutionGraph (Canonical Form)

All system execution is represented using a single immutable structure:

```json
ExecutionGraph = {
    "nodes": {
        "summary": {
            "type": "agent",
            "inputs": [],
            "outputs": ["summary_result"],
            "contracts": {
                "input_schema": {},
                "output_schema": {}
            }
        },
        "insights": {
            "type": "agent",
            "inputs": ["summary"],
            "outputs": ["insights_result"],
            "contracts": {
                "input_schema": {},
                "output_schema": {}
            }
        }
    },
    "edges": [
        ["summary", "insights"]
    ],
    "layers": [
        ["summary"],
        ["insights"]
    ]
}
```

### Key Invariants

* Nodes are **fully declarative**
* Edges define **strict dependency ordering**
* Layers are a **derived artifact only**
* No execution semantics exist inside graph definition
* Graph is immutable after validation

---

# 3. State Model (V7.7 Strict Contract State)

## 3.1 Global State Structure

```json
State = {
    "global_context": {},
    "artifacts": {},
    "node_outputs": {
        "summary": {},
        "insights": {}
    }
}
```

## 3.2 Hard Constraints

Each node MUST:

* Read from:

  * `global_context`
  * upstream `node_outputs`
* Write ONLY to:

  * `node_outputs[node_name]`

### Forbidden:

* Writing to other node outputs
* Implicit shared mutation
* Cross-node state mutation
* Global side effects

---

# 4. System Modules

---

## 4.1 graph_builder (NEW CORE)

### Responsibility

Transforms intent → ExecutionGraph

### Replaces:

* execution_order builder
* parallel grouping logic

### Output:

* Fully resolved DAG

### Contract:

```python
ExecutionGraph graph_builder(WorkflowIntent intent)
```

### Rules:

* Must not validate execution feasibility (delegated)
* Must not execute logic
* Must not assign runtime ordering semantics

---

## 4.2 graph_validator (UPGRADED)

### Responsibility

Ensures structural correctness of ExecutionGraph

### Validation Rules:

#### 1. DAG Integrity

* Cycle detection (mandatory)
* No self-loop edges

#### 2. Dependency Closure

* Every node input must map to a valid upstream node

#### 3. Forbidden Node Check

* Ensure no disallowed node types exist

#### 4. Layer Consistency

* Layers must respect topological ordering:

  * If A → B, then layer(A) < layer(B)

### Output:

```python
ValidationResult {
    "valid": bool,
    "errors": []
}
```

---

## 4.3 execution_engine (CORE RUNTIME)

### Responsibility

Deterministic execution of ExecutionGraph

### Execution Rules:

#### 1. Layer-by-Layer Execution

* Execute nodes strictly per layer order
* Within layer: parallel execution allowed (no dependencies)

#### 2. Node Isolation

* Each node receives:

  * snapshot state
* Each node produces:

  * isolated output

#### 3. State Commitment

* Output committed ONLY after successful node completion

#### 4. Failure Handling

* Node-level retry only
* Graph remains intact

---

## 4.4 state_contract system (NEW CRITICAL LAYER)

Each node MUST define:

```python
StateContract = {
    "INPUT_SCHEMA": {},
    "OUTPUT_SCHEMA": {},
    "STATE_REQUIREMENTS": {}
}
```

### Enforcement Rules:

* Input must validate before execution
* Output must validate before commit
* Invalid output = node failure
* No partial writes allowed

---

# 5. Execution Flow (V7.7 PIPELINE)

## Step 1 — Graph Construction

```text
Intent → graph_builder → ExecutionGraph
```

## Step 2 — Validation

```text
ExecutionGraph → graph_validator → ValidatedGraph
```

## Step 3 — Execution

```text
ValidatedGraph → execution_engine → FinalState
```

---

# 6. Retry Model (NODE-LEVEL ONLY)

## 6.1 Retry Definition

```text
retry(node) = re-execute node with frozen upstream snapshot
```

## 6.2 Properties

* No graph re-execution
* No state rollback beyond node boundary
* Deterministic replay guaranteed

## 6.3 Invalid Patterns Eliminated

* partial DAG rerun
* cascading retry effects
* global state corruption

---

# 7. Scheduler Redefinition

## OLD (V7.6)

* produces execution_order
* produces parallel groups

## NEW (V7.7)

* produces ExecutionGraph only
* no ordering logic
* no runtime semantics

Scheduler becomes purely declarative.

---

# 8. Eliminated Failure Classes

V7.7 structurally removes:

* UnboundLocalError (agent/result ambiguity)
* empty execution order crashes
* inconsistent parallel grouping
* retry-induced state corruption
* implicit ordering bugs
* shared-state race conditions

---

# 9. Migration Strategy

## Phase 1 — Dual System Coexistence

* Introduce ExecutionGraph
* Run in shadow mode alongside V7.6

## Phase 2 — Scheduler Migration

* Replace execution_order output with graph_builder output

## Phase 3 — Runtime Migration

* Replace run_graph with execution_engine

## Phase 4 — Decommission Legacy Engine

* Remove list-based execution completely
* Enforce graph-only runtime

---

# 10. Architectural Principle Summary

V7.7 enforces:

* **Structure first (Graph)**
* **Behavior second (Execution)**
* **State isolation per node**
* **No implicit ordering anywhere**
* **No shared mutable execution state**
* **Deterministic replay at node granularity**

---

If required, the next step is to define:

* Python reference implementation of ExecutionGraph
* graph_builder algorithm (topological + dependency resolver)
* execution_engine pseudocode (parallel-safe runtime)
* state_contract validation layer

These will fully operationalize V7.7 into production-grade runtime code.
