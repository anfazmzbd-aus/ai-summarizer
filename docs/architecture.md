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

  # Architecture Overview

## Runtime Lineage

V6.x
↓
V7.6 (Last Orchestration Runtime)
↓
V7.7 (Execution Runtime)
↓
V8.x (Future Extensions)

---

## Core Principles

### Graph Is Truth

Execution order is derived from graph.

No implicit sequencing.

---

### Runtime Is Stateless

Execution nodes cannot mutate shared state.

All writes:

state.node_outputs[node_name]

---

### Contracts Are Mandatory

Each node defines:

INPUT
OUTPUT
RETRY

Execution without contracts is invalid.

---

## Runtime Layers

graph_builder
↓
graph_validator
↓
execution_engine
↓
layer_executor
↓
node_executor
↓
state_merger

---

## Legacy Policy

Legacy runtime exists only under:

app/legacy/v76/

No production imports allowed.

#Final V7.7 import contract
main
↓
api
↓
service
↓
scheduler
↓
graph
↓
runtime
↓
registry
↓
state
↓
core

Final V7.7 Completion Set

Create these missing files.

app/
│
├── main.py
├── services/
│   └── summarize_service.py
│
├── api/
│   └── v1/
│       └── summarize_endpoint.py
│
├── orchestration/
│
│   ├── state/
│   │   ├── state_model.py
│   │   ├── state_builder.py
│   │   └── state_merger.py
│
│   ├── registry/
│   │   ├── agent_specs.py
│   │   └── agent_registry.py
│
│   ├── execution/
│   │   ├── execution_engine.py
│   │   └── retry_engine.py
│
│   ├── agents/
│   │   ├── summary.py
│   │   ├── insights.py
│   │   └── actions.py
│
└── tests/
    └── test_full_pipeline.py

##V7.7 Architecture Audit Report
Functional Correctness
Area	Status
GraphBuilder	✅ PASS
Scheduler	✅ PASS
Execution Engine	✅ PASS
Node Executor	✅ PASS
Layer Executor	✅ PASS
Agent Registry	✅ PASS
State Builder	✅ PASS
Contract Manager	✅ PASS
Response Builder	✅ PASS

Score:
10 / 10

DAG Integrity

Verified.

Summary
      │
      ▼
Insights

and

Summary
      │
      ▼
Actions

Layer ordering is deterministic.

No cycles.

No invalid execution.

Root/Leaf detection works.

Runtime

Verified.

Execution sequence

Scheduler

↓

GraphBuilder

↓

ExecutionGraph

↓

GraphValidator

↓

ExecutionEngine

↓

LayerExecutor

↓

NodeExecutor

↓

Agent

↓

Contract Validation

↓

State Merge

↓

ExecutionResponse

Exactly the runtime expected for V7.7.

API

Both APIs verified.

Legacy

POST /summarize

Playground

POST /playground/execute

Both produce identical execution.

Execution Result

Now returns

{
  execution_id
  status
  result
  node_outputs
  trace
  metrics
  errors
  metadata
}

Exactly what was intended.

Registry

Verified.

Registry is now the single source of truth.

GraphBuilder never hardcodes agents.

ExecutionEngine never knows about concrete agents.

Excellent separation.

Scheduler

Verified.

Scheduler only

selects agents
chooses strategy
builds graph

No execution logic remains.

Correct.

GraphBuilder

Produces

Nodes
Edges
Layers
Roots
Leaves

Exactly as designed.

Runtime Isolation

Verified.

ExecutionEngine owns execution.

LayerExecutor owns layers.

NodeExecutor owns nodes.

Agents own business logic.

State owns data.

Excellent separation.

Failure Tests

You intentionally broke

agent
registry
dependency
contract

System behaved correctly.

Recovery also verified.

This is important because it demonstrates that the architecture fails in predictable places rather than propagating corruption.

Test Suite
pytest

6 passed

Excellent.

Static Analysis
black

PASS

ruff

PASS

pre-commit

PASS

Excellent.

Git

Repository is in good shape.

Before tagging V7.7, I would:

remove obsolete files permanently
ensure deleted files are committed
exclude .vscode/ unless the settings are intentionally shared
avoid committing freeze_test.txt if it is only a temporary artifact
keep requirements_test.txt only if it has a defined role in CI/testing
Architecture Quality

I score projects using a production-readiness scale.

Category	Score
Modularity	10/10
Maintainability	10/10
Testability	10/10
Separation of Concerns	10/10
Determinism	10/10
Extensibility	10/10
Dependency Direction	10/10
Runtime Isolation	10/10
API Design	9.5/10
Documentation (current state)	7/10

Overall architecture:

9.8 / 10

The missing points are almost entirely documentation and production observability rather than architectural design.

V7.7-stable
                REST API
                    │
            SummarizeService
                    │
              Scheduler
                    │
             GraphBuilder
                    │
          ExecutionGraph
                    │
          GraphValidator
                    │
          ExecutionEngine
                    │
           LayerExecutor
                    │
            NodeExecutor
                    │
             AgentRegistry
                    │
               Agents
                    │
                 State
                    │
          ResponseBuilder

##V7.8-stable V1.0
=====================V7.8-stable========================
# AI Summarizer

# Architecture

Version: V7.8 Stable
Status: Production Ready Runtime Foundation

---

# Overview

AI Summarizer is a production-oriented, modular AI orchestration platform designed to execute AI agents deterministically through a validated execution graph.

The runtime separates planning from execution, allowing execution policies, observability, lifecycle management, caching, persistence, recovery, retries, middleware, and hooks to evolve independently.

The architecture emphasizes:

- Deterministic execution
- Strong separation of concerns
- Runtime extensibility
- Fault tolerance
- Testability
- Production readiness

---

# High-Level Architecture

```
                Request
                   │
                   ▼
          Intent Classification
                   │
                   ▼
           Strategy Builder
                   │
                   ▼
           Agent Selection
                   │
                   ▼
               Scheduler
                   │
                   ▼
          Execution Graph Builder
                   │
                   ▼
           Graph Validator
                   │
                   ▼
          Runtime Manager
                   │
                   ▼
          Runtime Session
                   │
                   ▼
          Runtime Context
                   │
     ┌─────────────┼────────────────┐
     │             │                │
     ▼             ▼                ▼
 Middleware     Hooks          Observers
     │             │                │
     └─────────────┼────────────────┘
                   │
                   ▼
          Execution Engine
                   │
         Layer Executor
                   │
         Node Executor
                   │
             AI Agents
```

---

# Runtime Components

## Runtime Manager

Responsibilities

- Owns execution lifecycle
- Creates RuntimeSession
- Creates RuntimeContext
- Coordinates Scheduler
- Coordinates ExecutionEngine
- Handles runtime state transitions

Location

```

app/runtime/runtime_manager.py

```

---

## Runtime Session

Represents one execution session.

Owns

- RuntimeContext
- RuntimeMetadata
- Execution identifiers

---

## Runtime Context

Contains execution state throughout the runtime lifecycle.

Responsibilities

- lifecycle state
- execution metadata
- configuration
- cancellation token
- metrics
- trace information

---

# Scheduling Layer

Scheduler converts user requests into executable graphs.

Responsibilities

- strategy selection
- graph construction
- execution planning

Output

ExecutionGraph

---

# Execution Graph

ExecutionGraph contains

```

Nodes
Edges
Execution Layers

```

The graph is validated before execution.

---

# Execution Engine

Responsible for deterministic graph execution.

Responsibilities

- execute graph layers
- invoke LayerExecutor
- emit execution events
- coordinate runtime execution

---

# Layer Executor

Executes one graph layer.

Supports

- sequential execution
- parallel execution

Updates

- state outputs
- execution artifacts

---

# Node Executor

Executes individual AI agents.

Responsibilities

- locate agent
- validate contracts
- execute agent
- collect outputs
- emit runtime events

Returns

NodeExecutionResult

---

# Runtime Events

Runtime emits strongly typed events.

Implemented events

```

ExecutionStarted
ExecutionFinished

LayerStarted
LayerFinished

NodeStarted
NodeFinished
NodeFailed

RetryStarted
RetryFinished

```

---

# Event Bus

Implements publish/subscribe messaging.

Responsibilities

- publish events
- dispatch subscribers
- decouple runtime components

---

# Subscribers

Current subscribers

## TraceSubscriber

Produces execution trace.

---

## MetricsSubscriber

Collects runtime metrics.

---

## LoggingSubscriber

Produces runtime logging.

---

# Runtime Observer

Observer provides passive monitoring.

Responsibilities

- observe lifecycle
- inspect runtime
- collect diagnostics

Observers never modify runtime behavior.

---

# Runtime Hooks

Hooks provide extension points.

Lifecycle

```

Before Runtime
After Runtime

```

Designed for

- plugins
- auditing
- external integrations

---

# Runtime Middleware

Middleware wraps execution.

Execution order

```

Middleware 1 Before
Middleware 2 Before

Execution

Middleware 2 After
Middleware 1 After

```

Used for

- authorization
- telemetry
- auditing
- request enrichment

---

# Runtime Policies

Policy Engine centralizes runtime decisions.

Examples

- retry policies
- timeout policies
- execution policies

---

# Retry System

RetryExecutor

Uses

RetryPolicy

Supports

- configurable attempts
- deterministic retries

---

# Timeout System

TimeoutExecutor

Supports

- execution timeout
- cancellation

---

# Cancellation

CancellationToken allows cooperative cancellation throughout execution.

---

# Circuit Breaker

Protects runtime from repeatedly failing operations.

States

```

Closed

Open

Half Open

```

Supports

- failure thresholds
- recovery timeout

---

# Execution Cache

Purpose

Reuse deterministic execution results.

Components

```

CacheEntry

CachePolicy

ExecutionCache

```

Supports

- TTL
- maximum entries
- eviction
- enable/disable

---

# Persistence

Stores execution history.

Components

```

ExecutionRecord

PersistenceManager

PersistenceBackend

MemoryBackend

```

Supports

- save
- load
- delete
- exists

Future

- SQLite
- PostgreSQL
- Redis
- Cloud Storage

---

# Checkpoint & Recovery

Supports resumable execution.

Components

```

Checkpoint

CheckpointManager

RecoveryManager

MemoryCheckpointBackend

```

Capabilities

- save checkpoints
- recover latest state
- future resume support

---

# Runtime State Flow

```

Initialize

↓

Scheduling

↓

Executing

↓

Completed

or

↓

Failed

```

---

# Directory Structure

```

app/

runtime/
cache/
checkpoint/
events/
hooks/
middleware/
observer/
persistence/

orchestration/
execution/
graph/
scheduler/

agents/

contracts/

tests/

```

---

# Testing

Current automated coverage

```

114 tests

```

Coverage includes

- execution
- runtime
- events
- middleware
- hooks
- observers
- cache
- persistence
- checkpointing
- recovery
- retries
- timeout
- circuit breaker
- API
- integration

All tests passing.

---

# Design Principles

The architecture follows these principles:

- Single Responsibility Principle
- Dependency Injection
- Composition over inheritance
- Event-driven communication
- Deterministic execution
- Immutable execution planning
- Runtime isolation
- Modular extensibility
- Test-first development
- Production readiness

---

# Current Status

Version

```

V7.8 Stable

```

Runtime Foundation Complete

Production Runtime Infrastructure Complete

Ready for

```

V7.9 Runtime Intelligence

```

##V7.8-stable V1.1
=====================V7.8-stable========================
# `ARCHITECTURE.md`

```markdown
# AI Summarizer Architecture

## Version

Current Version: **V7.8.0**

Architecture Status: **Production Runtime Foundation**

---

# 1. Vision

AI Summarizer is evolving from a document summarization application into a production-grade Agentic AI Runtime Platform.

The architecture is built around deterministic execution today, while preparing for adaptive runtime intelligence in future releases.

The guiding principles are:

- Modular architecture
- Strong separation of concerns
- Deterministic execution
- Extensible runtime
- Production reliability
- Enterprise scalability

---

# 2. High-Level Architecture

```

```
                    Client

                       │

               FastAPI / REST API

                       │

              Summarize Service

                       │

               Runtime Manager

                       │

              Runtime Session

                       │

              Runtime Context

                       │

    ┌──────────────────────────────────────┐
    │                                      │
    │  Middleware Pipeline                 │
    │  Runtime Hooks                       │
    │  Policy Engine                       │
    │  Runtime Observer                    │
    │                                      │
    └──────────────────────────────────────┘

                       │

                  Scheduler

                       │

               ExecutionGraph

                       │

              Execution Engine

                       │

              Layer Executor

                       │

              Node Executor

                       │

               Registered Agents

                       │

             Response Builder
```

```

---

# 3. Architectural Layers

```

Presentation Layer
│
Application Layer
│
Runtime Layer
│
Execution Layer
│
Agent Layer
│
Infrastructure Layer

```

---

# 4. Runtime Layer

Location

```

app/runtime/

```

The Runtime Layer owns execution lifecycle and production behavior.

Responsibilities

- Runtime lifecycle
- Execution orchestration
- Reliability
- Runtime policies
- Observability
- Extension points
- Runtime state

Core Components

```

RuntimeManager
RuntimeSession
RuntimeContext
RuntimeConfig
RuntimeMetadata
CancellationToken

```

---

# 5. Execution Layer

Location

```

app/orchestration/

```

Responsible for deterministic workflow execution.

Core Components

```

Scheduler
ExecutionGraph
ExecutionEngine
LayerExecutor
NodeExecutor
ContractManager
StateBuilder

```

Responsibilities

- Build execution graph
- Validate DAG
- Execute nodes
- Execute layers
- Maintain execution state
- Preserve execution order

---

# 6. Agent Layer

Location

```

app/agents/

```

Agents perform domain-specific AI tasks.

Examples

```

Summary Agent
Insight Agent
Trend Agent
Risk Agent
Sentiment Agent
Forecast Agent
Recommendation Agent

```

Agent responsibilities

- Execute a specialized task
- Produce deterministic output
- Never orchestrate execution
- Never control runtime behavior

---

# 7. Runtime Event Architecture

Location

```

app/runtime/events/

```

Components

```

EventBus
EventDispatcher
RuntimeEventPublisher
SubscriberRegistry
EventTypes

```

Current Events

```

ExecutionStarted
ExecutionFinished

LayerStarted
LayerFinished

NodeStarted
NodeFinished
NodeFailed

RetryStarted
RetryFinished

```

Purpose

- Runtime observability
- Event-driven extensions
- Metrics
- Logging
- Tracing

---

# 8. Runtime Observability

Location

```

app/runtime/observer/

```

Components

```

RuntimeObserver
ObserverContext

```

Subscribers

```

LoggingSubscriber
MetricsSubscriber
TraceSubscriber

```

Responsibilities

- Runtime monitoring
- Execution tracing
- Metrics collection
- Structured logging

---

# 9. Reliability Layer

## Retry

```

RetryExecutor
RetryPolicy

```

Supports configurable retry behavior.

---

## Timeout

```

Timeout
TimeoutExecutor

```

Supports execution timeout protection.

---

## Circuit Breaker

```

CircuitBreaker

```

Protects the runtime against repeated failures.

---

## Cancellation

```

CancellationToken

```

Supports cooperative execution cancellation.

---

# 10. Runtime Extension Framework

## Middleware

Location

```

app/runtime/middleware/

```

Components

```

RuntimeMiddleware
MiddlewarePipeline

```

Responsibilities

- Pre-execution processing
- Post-execution processing
- Cross-cutting concerns

---

## Runtime Hooks

Location

```

app/runtime/hooks/

```

Components

```

RuntimeHook
HookManager
HookContext

```

Responsibilities

- Runtime lifecycle callbacks
- Extension points
- Custom runtime behavior

---

# 11. Policy Engine

Location

```

app/runtime/policy/

```

Component

```

PolicyEngine

```

Purpose

Evaluate runtime policies before execution.

Examples

- Retry decisions
- Timeout policy
- Runtime restrictions
- Execution behavior

---

# 12. Runtime Cache

Location

```

app/runtime/cache/

```

Components

```

ExecutionCache
CacheEntry
CachePolicy

```

Capabilities

- TTL expiration
- Entry eviction
- Maximum cache size
- Execution output caching

---

# 13. Execution Persistence

Location

```

app/runtime/persistence/

```

Components

```

ExecutionRecord
PersistenceBackend
MemoryBackend
PersistenceManager

```

Responsibilities

- Store execution history
- Persist runtime metadata
- Abstract storage backend

---

# 14. Checkpoint & Recovery

Location

```

app/runtime/checkpoint/

```

Components

```

Checkpoint
MemoryCheckpointBackend
CheckpointManager
RecoveryManager

```

Capabilities

- Save execution state
- Resume interrupted execution
- Recover runtime state

---

# 15. Runtime State Flow

```

Request

│

RuntimeManager

│

RuntimeSession

│

RuntimeContext

│

Scheduler

│

ExecutionGraph

│

ExecutionEngine

│

LayerExecutor

│

NodeExecutor

│

Agent

│

State Update

│

Response Builder

│

Response

```

---

# 16. Runtime Lifecycle

```

INITIALIZING

```
  │
```

SCHEDULING

```
  │
```

EXECUTING

```
  │
```

COMPLETED

```
  │
```

FAILED (if required)

```
  │
```

TERMINATED

```

---

# 17. Testing Status

Current Validation

```

114 Unit Tests

```

Validation Pipeline

```

Black

↓

Ruff

↓

Pytest

```

Current Status

```

114 Passed

Black Passed

Ruff Passed

Pytest Passed

```

---

# 18. Design Principles

## Separation of Concerns

Runtime owns orchestration.

Agents own execution.

---

## Deterministic Execution

ExecutionGraph is the execution contract.

Execution order is reproducible.

---

## Extensibility

New functionality should be added using:

- Middleware
- Hooks
- Policies
- Subscribers

Avoid modifying the execution engine unless necessary.

---

## Reliability

Runtime must support

- Retry
- Timeout
- Circuit breaker
- Recovery
- Checkpointing
- Persistence

---

## Observability

Every execution should be observable through:

- Events
- Logging
- Metrics
- Tracing

---

## Testability

Every production component requires

- Unit tests
- Integration tests
- Regression coverage

---

# 19. Architectural Rules

The following rules are mandatory.

Rule 1

ExecutionGraph is the single orchestration contract.

---

Rule 2

ExecutionEngine is the only execution coordinator.

---

Rule 3

Runtime controls execution.

Agents never control runtime.

---

Rule 4

All runtime extensions use official extension points.

- Middleware
- Hooks
- Policies
- Event subscribers

---

Rule 5

Every new capability requires:

- Implementation
- Tests
- Documentation
- Integration validation

---

# 20. V7.9 Architecture Direction

The V7.8 architecture becomes the stable foundation for V7.9.

The next evolution introduces intelligent runtime behavior while preserving all existing execution infrastructure.

Planned additions

```

Runtime Intelligence

↓

Dynamic Planning

↓

Agent Selection

↓

Runtime Learning

↓

Distributed Execution

```

The following components remain stable and are not expected to be rewritten during V7.9:

- RuntimeManager
- RuntimeSession
- RuntimeContext
- Scheduler
- ExecutionGraph
- ExecutionEngine
- LayerExecutor
- NodeExecutor
- EventBus
- RuntimeObserver
- ExecutionCache
- PersistenceManager
- CheckpointManager
- RecoveryManager

Future development should extend these components rather than replace them.

---

# Architecture Baseline

**Version:** V7.8.0

**Status:** Stable Production Runtime Foundation

**Validation:**

- 114/114 tests passing
- Black passing
- Ruff passing
- Pytest passing

This document defines the official architectural baseline from which all V7.9 development should proceed.
```

---

## Documentation Package Complete

The documentation set is now complete and internally consistent:

* ✅ `ARCHITECTURE.md`
* ✅ `CHANGELOG.md`
* ✅ `PROJECT_STATUS.md`
* ✅ `ROADMAP.md`
* ✅ `V7.8_TO_V7.9_TRANSITION_PACKAGE.md`

Together with your passing validation (`114` tests, `black`, `ruff`, and `pytest` all green), this establishes **V7.8.0** as the frozen production baseline. The next chat can begin directly with **V7.9 Phase 1 – Adaptive Runtime Intelligence**, using the transition package as the authoritative context to preserve continuity and prevent architectural drift.

##V7.9-phase 1

* Adaptive Runtime Intelligence layer

    Adaptive Runtime Intelligence
    ─────────────────────────────

    Architecture                     ✅

    Domain Contracts                 ✅
        strategy_types.py
        execution_strategy.py
        reasoning_result.py
        decision.py

    RuntimeReasoner                  ✅

    StrategySelector                 ✅

    DecisionEngine                   ✅

    Integration Tests                ✅

    Repository Validation            ✅

    Repository baseline:
      181 tests passing
      black passing
      pre-commit passing

* RuntimeReasoner
* StrategySelector
* DecisionEngine
* Updated architecture diagram
* Runtime decision flow


  # AI Summarizer Architecture

  ## Overview

  AI Summarizer is a production-oriented AI execution platform built around:

  - Agent-based processing
  - Graph-based orchestration
  - Deterministic execution
  - Adaptive runtime intelligence
  - Runtime observability
  - Diagnostics
  - Execution reporting

  The platform evolved from a simple summarization service into an extensible agentic execution runtime.

  # Architecture Evolution

  ## V1-V5: Application Foundation

  Introduced:

  - FastAPI service
  - Persistence layer
  - Modular application structure
  - Multi-output analysis


  ## V6: Agent Architecture

  Introduced:

  - Agent registry
  - Intent classification
  - Semantic routing
  - Dependency graphs


  ## V7: Execution Runtime

  Introduced:

  - ExecutionGraph
  - Scheduler
  - ExecutionEngine
  - Layer execution
  - State contracts


  ## V7.8: Production Runtime Foundation

  Introduced:

  - Runtime lifecycle management
  - Runtime context
  - Events
  - Middleware
  - Hooks
  - Policies
  - Cache
  - Persistence
  - Checkpoints


  ## V7.9: Adaptive Runtime Platform

  Introduced:

  - Runtime intelligence
  - Adaptive execution decisions
  - Observability pipeline
  - Diagnostics
  - Reporting

# V7.9 Architecture

The system is organized into independent layers.
Architecture diagram:
                    API Layer

                       |

              Runtime Manager

                       |

              Runtime Session

                       |

              Runtime Context

                       |

        +--------------+--------------+

        |                             |

 Runtime Intelligence          Execution Runtime

        |                             |

 Decision Engine              Execution Graph

 Strategy Selector             Scheduler

 Runtime Reasoner              Execution Engine

                                      |

                               Layer Executor

                                      |

                               Node Executor

                                      |

                                  Agents


                                      |

                         Observability / Diagnostics

                                      |

                               Reporting Layer


# Runtime Architecture

The runtime layer owns execution lifecycle management.

## RuntimeManager

Responsibilities:

- Runtime entry point
- Lifecycle coordination
- Execution delegation


## RuntimeSession

Responsibilities:

- Single execution ownership
- Runtime object aggregation
- State isolation


## RuntimeContext

Responsibilities:

- Runtime-scoped access
- Metadata exposure
- Execution lifecycle state


## RuntimeMetadata

Stores:

- Execution status
- Timestamps
- Observability references
- Diagnostics
- Reports

# Execution Lifecycle

A runtime execution follows:
Request

↓

RuntimeManager

↓

Create RuntimeSession

↓

Initialize RuntimeContext

↓

Runtime Intelligence

↓

Create Execution Decision

↓

Scheduler

↓

ExecutionGraph

↓

ExecutionEngine

↓

LayerExecutor

↓

NodeExecutor

↓

Agents

↓

Runtime Snapshot

↓

Diagnostics

↓

Runtime Report

# Runtime Intelligence

Runtime intelligence determines execution behaviour.

Components:

## Runtime Reasoner

Analyzes runtime conditions.

Examples:

- Workload size
- Parallel opportunities
- Cache availability
- Retry requirements


## Strategy Selector

Chooses execution strategy.


## Decision Engine

Produces runtime execution decisions.


## Execution Strategy

Defines:

- Parallel execution
- Cache usage
- Retry behaviour
- Checkpoint behaviour
- Timeout behaviour

# Observability

Observability provides runtime visibility.

Components:

- ExecutionMetrics
- ExecutionTimeline
- RuntimeSnapshot


Provides:

- Execution timing
- Layer tracking
- Runtime state capture

# Diagnostics

Diagnostics analyse runtime execution results.

Components:

- RuntimeDiagnostics
- ExecutionAnalyzer
- ExecutionStatistics
- FailureClassifier


Provides:

- Health evaluation
- Failure analysis
- Runtime issues

# Reporting

Reporting converts runtime state into consumable output.

Components:

- RuntimeReport
- ExecutionSummary
- RuntimeHealth
- ReportBuilder


Consumers:

- API responses
- Dashboards
- Logs
- Future monitoring systems

10. Component Responsibilities
# Dependency Rules

The architecture follows one-directional dependency flow.

Allowed:
Execution
↓
Observability
↓
Diagnostics
↓
Reporting

Runtime intelligence influences execution but does not own execution.

Forbidden:

- Reporting importing ExecutionEngine
- Diagnostics mutating execution state
- Observability controlling execution
- Agents accessing RuntimeManager directly

# Testing Architecture

V7.9 maintains layered validation.

Coverage:

## Unit Tests

Validate:

- Intelligence components
- Runtime models
- Observability
- Diagnostics
- Reporting


## Integration Tests

Validate:

- Runtime lifecycle
- Adaptive execution
- Runtime pipeline


Current coverage:
237 tests passing

Quality gates:

- Black
- Ruff
- Pytest
- Pre-commit

# Extension Points

Future extensions should integrate through:

- Runtime middleware
- Runtime hooks
- Event subscribers
- Policy engine
- Reporting adapters

New capabilities should avoid modifying:

- ExecutionGraph
- ExecutionEngine
- Core runtime lifecycle
