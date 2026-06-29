# Architecture

## Overview

AI Summarizer is an Agent-Oriented Document Processing Platform built on FastAPI.

The platform processes documents through a graph-based orchestration engine.

---

# High-Level Flow

Document
↓
Intent Classifier
↓
Strategy Builder
↓
Semantic Router
↓
Dependency Resolver
↓
Parallel Execution Engine
↓
Agent Registry
↓
Agents
↓
Execution Metadata

---

# Core Components

## Agent Service

Entry point for orchestration.

Responsibilities:

* Build state
* Execute graph
* Return result

File:

app/services/agent_service.py

---

## Agent Graph

Core orchestration engine.

Responsibilities:

* Intent classification
* Strategy building
* Semantic routing
* Dependency resolution
* Parallel execution
* Metadata collection

File:

app/services/agent_graph.py

---

## Agent Registry

Central registry of available agents.

File:

app/services/registry/agent_registry.py

---

## State Model

Shared state object used by all agents.

File:

app/services/agent_state.py

---

## Database Layer

Stores:

* Input text
* Agent output
* Execution metadata

Files:

app/db/models.py

app/services/db_service.py

---

## Presentation Layer

FastAPI Routes

Templates

Static Assets

production-grade V7.5 documentation update

V7.5.0 STABLE ARCHITECTURE
Overview

The AI Summarizer is a multi-agent DAG-based execution engine that transforms raw input into structured analytical outputs using parallel agent orchestration.

Core Pipeline
Input Text
    ↓
Semantic Router (intent detection)
    ↓
Section Parser (structuring input)
    ↓
Dependency Resolver (DAG construction)
    ↓
Graph Validator (consistency check)
    ↓
Parallel Scheduler (execution grouping)
    ↓
Parallel Executor (agent execution)
    ↓
Artifact Aggregation (state merge)
    ↓
Response Formatter
    ↓
History Persistence (DB)

Agent Registry System
All agents are dynamically registered:
AGENT_REGISTRY = {
    "summary": {...},
    "insights": {...},
    "trend": {...},
    "sentiment": {...},
    "findings": {...},
    "risk": {...},
    "root_cause": {...},
    "forecast": {...},
    "recommendation": {...},
    "plan": {...}
}

Dependency Model (DAG)

Execution order is derived using:

semantic routing
dependency resolution
graph validation
Example DAG:
summary
  ↓
insights → sentiment → findings
  ↓
trend → risk
  ↓
forecast → root_cause
  ↓
recommendation

Parallel Execution Model

Agents are grouped into execution layers:
Layer 1:
  summary

Layer 2:
  insights, findings, sentiment

Layer 3:
  trend, risk

Layer 4:
  forecast, root_cause

Layer 5:
  recommendation

Each layer executes concurrently.

Output Structure

Each run produces:

{
  "summary": "",
  "insights": [],
  "findings": [],
  "trend": [],
  "sentiment": [],
  "risk": [],
  "forecast": [],
  "root_cause": [],
  "recommendations": [],
  "execution_plan": {},
  "execution_metadata": {}
}

V7.6 Production Architecture

┌────────────────────────────────────────────────────────────┐
│                      CLIENT / UI LAYER                     │
│  Web UI • API • Upload PDF • Future Integrations           │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│                    REQUEST ENTRY LAYER                     │
│                     routes/summarize.py                    │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
══════════════════ PREPROCESSING (NOT DAG) ═══════════════════

┌────────────────────────────────────────────────────────────┐
│                  INPUT NORMALIZATION                       │
│  • Clean text                                              │
│  • Token metrics                                           │
│  • Upload extraction                                       │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼

┌────────────────────────────────────────────────────────────┐
│                    SUMMARY GENERATION                      │
│                   summary_agent (NON-DAG)                  │
│                                                            │
│ OUTPUT:                                                    │
│ state["summary"]                                           │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼

┌────────────────────────────────────────────────────────────┐
│                     SECTION PARSER                         │
│            app/services/context/section_parser.py          │
│                                                            │
│ OUTPUT:                                                    │
│ state["plan"]["sections"]                                  │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼

┌────────────────────────────────────────────────────────────┐
│                    SEMANTIC ROUTER                         │
│                     semantic_router.py                     │
│                                                            │
│ OUTPUT:                                                    │
│ selected_agents                                            │
│ execution strategy                                         │
└───────────────────────┬────────────────────────────────────┘
                        |
                        ▼

══════════════════════ DAG ENGINE (V7.6) ══════════════════════

                        │
                        ▼

┌────────────────────────────────────────────────────────────┐
│                 DEPENDENCY RESOLVER                        │
│         resolve_execution_order()                          │
└───────────────────────┬────────────────────────────────────┘
                        |
                        ▼

┌────────────────────────────────────────────────────────────┐
│                    GRAPH VALIDATOR                         │
│            validate_execution_graph()                      │
│                                                            │
│ Checks:                                                    │
│ • unknown agents                                           │
│ • dependency violations                                    │
│ • DAG purity                                               │
└───────────────────────┬────────────────────────────────────┘
                        |
                        ▼

┌────────────────────────────────────────────────────────────┐
│                    SCHEDULER (NEW)                         │
│                  scheduler.py                              │
│                                                            │
│ OUTPUT:                                                    │
│ parallel_groups                                            │
└───────────────────────┬────────────────────────────────────┘

                        ▼

┌────────────────────────────────────────────────────────────┐
│                 PARALLEL EXECUTOR                          │
│               parallel_executor.py                         │
└───────────────────────┬────────────────────────────────────┘
                        |
                        ▼

┌────────────────────────────────────────────────────────────┐
│                     DAG AGENTS                             │
│                                                            │
│ insights → findings → sentiment                            │
│            ↓                                               │
│          trend → risk                                      │
│            ↓                                               │
│         forecast → root_cause                              │
│            ↓                                               │
│      recommendation                                        │
└───────────────────────┬────────────────────────────────────┘
                        |
                        ▼

════════════════════ RUNTIME + OUTPUT ════════════════════════
                        |
                        ▼

┌────────────────────────────────────────────────────────────┐
│                     STATE MERGER                           │
│                                                            │
│ state["artifacts"]                                         │
└───────────────────────┬────────────────────────────────────┘
                        |
                        ▼

┌────────────────────────────────────────────────────────────┐
│                  RESPONSE FORMATTER                        │
│                                                            │
│ Summary                                                    │
│ Artifacts                                                  │
│ Execution Plan                                             │
│ Execution Metadata                                         │
└───────────────────────┬────────────────────────────────────┘
                        |
                        ▼

┌────────────────────────────────────────────────────────────┐
│                  STORAGE / HISTORY                         │
│               DB + Observability                           │
└────────────────────────────────────────────────────────────┘

Production Boundaries
Layer A — Request Processing
  routes/
  upload handling
  input validation
Layer B — Preprocessing (outside DAG)
  summary
  section parsing
  routing
Layer C — Execution Engine
  resolver
  validator
  scheduler
  executor
Layer D — Runtime
  artifacts
  merge
  metadata
Layer E — Delivery
  formatter
  persistence
V7.6 Design Principles
  Summary is precomputed, never scheduled
  Planner decides what to run
  Scheduler decides when to run
  Executor decides how to run
  Runtime decides how to merge

V7.6 is now behaving like a real DAG runtime:

  Preprocessing
  ↓
  Planning
  ↓
  Validation
  ↓
  Scheduling
  ↓
  Parallel Execution
  ↓
  Retry
  ↓
  Immutable Merge
  ↓
  Artifacts

  No architectural contamination visible in this output anymore.

  ✅ Execution Plan ↔ Execution Metadata are synchronized

  Execution Plan:

  execution_order:
  [
  'sentiment',
  'actions',
  'findings',
  'insights',
  'risk',
  'trend',
  'forecast',
  'root_cause',
  'recommendation'
  ]

  Execution Metadata:

  agents_executed:
  [
  'sentiment',
  'actions',
  'findings',
  'insights',
  'risk',
  'trend',
  'forecast',
  'root_cause',
  'recommendation'
  ]

  ✅ Parallel scheduling is deterministic

  Plan:

  parallel_groups:
  [
  ['sentiment','actions','findings','insights'],
  ['risk','trend'],
  ['forecast','root_cause'],
  ['recommendation']
  ]

  Runtime:

  parallel_groups:
  [
  ['sentiment','actions','findings','insights'],
  ['risk','trend'],
  ['forecast','root_cause'],
  ['recommendation']
  ]

  Perfect.

  Scheduler → executor → metadata are now using the same ordering model.

  ✅ Deterministic merge appears healthy

  Trace sample output:

  artifacts:
  {
  sentiment,
  actions,
  findings,
  insights,
  risk,
  trends,
  forecasts,
  root_causes,
  recommendations
  }

  No nested artifact contamination anymore

  V7.6
  STATUS = STABLE
  Scheduler = OK
  Validator = OK
  Retry = OK
  Merger = OK
  Traceability = OK
  DAG Isolation = OK

  V7.7 — Execution Engine Evolution Plan (Clean Architecture Layer)

  🧠 Key Architectural Rules (V7.7)
    1. Hard Separation of Responsibilities
    Layer	Responsibility
    graph_builder	builds execution structure only
    graph_validator	validates correctness only
    execution_engine	runs everything
    state_model	defines truth of data
    scheduler	orchestration planning only

    2. Execution Rule (CRITICAL)
    NO agent decides order
    NO runtime builds dependencies
    NO list-based execution logic outside graph

    Only:

    ExecutionGraph → ExecutionEngine → Output

  3. State Rule

    Each node writes ONLY to:

    state.node_outputs[agent_name]

    No cross writes allowed.

  4. Retry Rule

    Retry operates on:

    node + snapshot_state

    NOT full pipeline.

  5. Preprocessing Isolation
    preprocessing/
        summary_agent.py
    runs before graph
    never enters ExecutionGraph
    never validated by DAG rules

  6. Why this structure is “production-grade”

    Because it guarantees:

    ✔ Deterministic execution
    ✔ No hidden coupling between agents
    ✔ No runtime graph mutation
    ✔ Fully testable DAG layer
    ✔ Isolated retries (critical for reliability)
    ✔ Clear observability boundaries








🧠 V7.7 Production Folder Structure

  app/
  │
  ├── routes/
  │   ├── summarize.py
  │   ├── health.py
  │
  ├── core/
  │   ├── config.py
  │   ├── constants.py
  │   ├── exceptions.py
  │
  ├── orchestration/
  │   │
  │   ├── graph/
  │   │   ├── graph_builder.py              # NEW: builds ExecutionGraph
  │   │   ├── graph_schema.py              # NEW: ExecutionGraph dataclass / schema
  │   │   ├── graph_validator.py           # upgraded DAG + contract validation
  │   │   ├── graph_optimizer.py          # optional (future: pruning, batching)
  │   │
  │   ├── execution/
  │   │   ├── execution_engine.py         # NEW CORE: replaces run_graph
  │   │   ├── layer_executor.py           # executes parallel layers
  │   │   ├── node_executor.py            # executes single agent node
  │   │   ├── retry_engine.py             # node-level retry system
  │   │
  │   ├── scheduler/
  │   │   ├── scheduler.py                # now ONLY builds graph
  │   │
  │   ├── state/
  │   │   ├── state_model.py              # canonical State object
  │   │   ├── state_builder.py            # builds initial state
  │   │   ├── state_merger.py             # immutable merge logic (V7.6 upgraded)
  │   │   ├── state_contracts.py          # INPUT/OUTPUT schema per agent
  │   │
  │   ├── intent/
  │   │   ├── intent_classifier.py
  │   │   ├── intent_router.py
  │   │
  │   ├── strategy/
  │   │   ├── strategy_builder.py
  │   │   ├── agent_selector.py
  │   │
  │   ├── preprocessing/
  │   │   ├── summary_agent.py            # ONLY preprocessing node
  │   │   ├── section_parser.py
  │   │
  │   ├── agents/
  │   │   ├── insights.py
  │   │   ├── actions.py
  │   │   ├── sentiment.py
  │   │   ├── findings.py
  │   │   ├── trend.py
  │   │   ├── risk.py
  │   │   ├── root_cause.py
  │   │   ├── forecast.py
  │   │   ├── recommendation.py
  │   │
  │   ├── registry/
  │   │   ├── agent_registry.py           # metadata + dependencies + contracts
  │   │
  │   ├── logging/
  │   │   ├── logger.py
  │   │   ├── trace_logger.py
  │   │
  │   ├── observability/
  │   │   ├── metrics.py
  │   │   ├── execution_trace.py
  │   │   ├── debug_dump.py
  │
  ├── api/
  │   ├── api_v1/
  │   │   ├── summarize_endpoint.py
  │
  ├── tests/
  │   ├── test_graph_builder.py
  │   ├── test_execution_engine.py
  │   ├── test_state_merger.py
  │   ├── test_retry_engine.py
  │
  └── main.py