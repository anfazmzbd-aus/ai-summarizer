# AI Summarizer

## Overview

AI Summarizer is an Agent-Based Document Processing and Summarization Platform built with FastAPI.

The project started as a simple text summarizer and evolved into a graph-driven agent orchestration system capable of:

* Semantic document routing
* Multi-intent classification
* Agent selection
* Dependency-aware execution
* Parallel agent execution
* Execution tracking and explainability

Current Version: **V6.7.1 Stable**

---

# Architecture

```text
Document
    ↓
Intent Classifier
    ↓
Multi-Intent Planner
    ↓
Strategy Builder
    ↓
Semantic Router
    ↓
Dependency Resolver
    ↓
Parallel Execution Graph
    ↓
Agent Registry
    ↓
Agents
    ↓
Execution Metadata
```

---

# Features

## Summarization

Generates concise summaries from input text.

## Action Extraction

Identifies tasks and follow-up actions.

Examples:

* should
* must
* need to
* follow up

## Business Insights

Detects:

* Revenue changes
* Profit improvements
* Market expansion

## Research Findings

Detects:

* Research content
* Studies
* Analysis
* Results

## Multi-Intent Detection

A document can belong to multiple categories simultaneously.

Example:

```text
Meeting Notes
Business Report
Research Report
```

## Semantic Routing

Automatically selects the required agents based on content analysis.

## Dependency Graph

Agents can declare dependencies.

Example:

```text
summary
   ├── actions
   ├── insights
   └── findings
```

## Parallel Execution

Independent agents execute concurrently to improve performance.

---

# Project Structure

```text
ai-summarizer/
│
├── main.py
├── tools.py
│
├── app/
│   ├── routes/
│   │   ├── home.py
│   │   ├── summarize.py
│   │   ├── upload.py
│   │   └── history.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── services/
│   │   ├── agent_service.py
│   │   ├── agent_graph.py
│   │   ├── db_service.py
│   │   │
│   │   ├── agents/
│   │   │   ├── summary_agent.py
│   │   │   ├── actions_agent.py
│   │   │   ├── insights_agent.py
│   │   │   ├── findings_agent.py
│   │   │   ├── plan_agent.py
│   │   │   └── trend_agent.py
│   │   │
│   │   ├── registry/
│   │   │   ├── registry.py
│   │   │   └── agent_registry.py
│   │   │
│   │   ├── classifiers/
│   │   │   └── intent_classifier.py
│   │   │
│   │   ├── strategies/
│   │   │   └── strategy_builder.py
│   │   │
│   │   ├── routers/
│   │   │   └── semantic_router.py
│   │   │
│   │   └── graph/
│   │       ├── dependency_resolver.py
│   │       ├── parallel_groups.py
│   │       ├── parallel_executor.py
│   │       └── agent_runner.py
│   │
│   └── state/
│       └── agent_state.py
│
├── templates/
│   ├── home.html
│   ├── history.html
│   └── result.html
│
├── requirements.txt
└── README.md
```

---

# Agent Registry

Agents self-register using decorators.

Example:

```python
@register_agent(
    "insights",
    depends_on=["summary"]
)
def insights_agent(state):
    ...
```

---

# Execution Metadata

Every run records:

```python
{
    "agents_executed": [],
    "agent_count": 0,
    "parallel_groups": [],
    "timings": {}
}
```

Example:

```python
{
    "agents_executed": [
        "summary",
        "actions",
        "insights",
        "findings"
    ],
    "agent_count": 4,
    "parallel_groups": [
        ["summary"],
        ["actions", "insights", "findings"]
    ],
    "timings": {
        "summary": 0.000005,
        "actions": 0.000456,
        "insights": 0.000286,
        "findings": 0.000127
    }
}
```

---

# Running the Application

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

# Current Version

## V6.7.1 Stable

Completed:

* Agent State
* Agent Graph
* Agent Registry
* Intent Classification
* Multi-Intent Routing
* Semantic Planning
* Dependency Resolution
* Parallel Execution
* Execution Tracking
* Explainability

---

# Roadmap

## V6.8

Tool-Enabled Agents

* action_tool
* trend_tool
* finding_tool
* keyword_tool
* sentiment_tool

## V6.9

LLM-Based Planning

* Dynamic planning
* Agent selection via LLM
* Tool selection via LLM

## V7

Agentic AI Summarization Platform

* Full workflow orchestration
* Tool ecosystem
* Agent memory
* Multi-document analysis
* Enterprise reporting
* Human-in-the-loop review

```
```
Current Architectural Version

Your codebase is now effectively:

V6.7.1 Stable

✓ Agent Registry
✓ Semantic Routing
✓ Intent Classification
✓ Multi Intent Detection
✓ Dependency Graph
✓ Parallel Execution
✓ Execution Metadata
✓ Database Persistence

# why summarizer.py still exists.

It is not acting as the FastAPI startup file.

It is acting as a shared AI model module.

# Better Structure (V6.7.2 Cleanup)

Create:

app/
└── models/
    └── summarizer_model.py

Then update:

# app/services/agents/summary_agent.py

# Current State

Previously:

summarizer.py
├── summarizer_model
└── implicit dependency for summary_agent

Now:

summary_agent.py
    ↓
app/models/summarizer_model.py

(or whatever path you chose)

and startup is:

uvicorn app.main:app --reload

So summarizer.py is no longer part of the runtime path.

# Updated V6.7.1 Structure

A cleaner representation of your current architecture would be:

ai-summarizer/
│
├── requirements.txt
├── README.md
├── tools.py
├── __init__.py
│
├── static/
│   ├── style.css
│   └── app.js
│
├── docs/
│   ├── architecture.md
│   └── roadmap.md
|
├── logs/
|   |
│   └── app.log
|
└── app/
    │
    ├── __init__.py
    ├── main.py
    │
    ├── models/
    |   ├── __init__.py
    │   └── summarizer_model.py
    │
    ├── templates/
    |   ├── __init__.py
    │   ├── home.html
    │   ├── history.html
    │   └── result.html
    │
    ├── routes/
    |   ├── __init__.py
    │   ├── home.py
    │   ├── summarize.py
    │   ├── upload.py
    │   └── history.py
    │
    ├── db/
    |   ├── __init__.py
    │   ├── database.py
    │   └── models.py
    │
    └── services/
        │
        ├── __init__.py
        ├── agent_service.py
        ├── agent_graph.py
        ├── agent_state.py
        ├── db_service.py
        │
        ├── agents/
        │   ├── __init__.py
        │   ├── summary_agent.py
        │   ├── actions_agent.py
        │   ├── insights_agent.py
        │   ├── findings_agent.py
        │   ├── plan_agent.py
        │   └── trend_agent.py
        │
        ├── registry/
        |   ├── __init__.py
        │   ├── registry.py
        │   └── agent_registry.py
        │
        ├── classifiers/
        |   ├── __init__.py
        │   └── intent_classifier.py
        │
        ├── strategies/
        |   ├── __init__.py
        │   └── strategy_builder.py
        │
        ├── routers/
        |   ├── __init__.py
        │   └── semantic_router.py
        │
        └── graph/
            ├── __init__.py
            ├── dependency_resolver.py
            ├── parallel_groups.py
            ├── parallel_executor.py
            └── agent_runner.py

# because you've now validated:

Intent Classification
Semantic Routing
Agent Registry
Dependency Resolution
Parallel Execution
Execution Metadata
FastAPI Integration

This is the first version that resembles a true orchestration engine rather than a simple summarizer.

V6.7

parallel_groups:
[
 ["summary"],
 ["insights","actions"],
 ["trend","risk"]
]

summary = preprocessing
metadata agent_count includes preprocessing
agents_executed excludes preprocessing

V7.7 — Execution Engine Evolution Plan (Clean Architecture Layer)
  Core Goal of V7.7

    Transform this:

    “Agent orchestration system”

    into:

    “Deterministic DAG execution runtime with state contracts”

# AI-Summarizer — Runtime Status

## Current Runtime

Active Runtime: **V7.7 Graph-Based Execution Engine**

Status:

* ExecutionGraph operational
* Deterministic execution enabled
* Contract-based runtime enabled
* Full pipeline tests passing

---

## Runtime Evolution

### V7.6 (Archived Runtime)

Architecture:

* Scheduler → execution_order
* Parallel groups
* Mutable execution state
* Runtime-driven orchestration

Status:

* Frozen
* Maintained for rollback only
* No future feature development

---

### V7.7 (Current Runtime)

Architecture:

* Scheduler → ExecutionGraph
* GraphValidator
* ExecutionEngine
* State Contracts
* Node-level retries

Execution Model:

Request
→ Scheduler
→ ExecutionGraph
→ ExecutionEngine
→ State
→ Output

---

## Development Policy

New features MUST target V7.7.

Do not introduce:

* execution_order
* parallel_groups
* runtime dependency generation

All execution must originate from ExecutionGraph.

Development

pytest

uvicorn app.main:app --reload

pre-commit run --all-files

## AI Summarizer
## Version: V7.7 Stable
Update:

Project Overview
Features
Architecture
Folder Structure
Execution Pipeline
Scheduler
Execution Engine
Runtime
API
Tests
Future Roadmap

========================================================================

# AI Summarizer

A production-oriented AI orchestration platform built around graph-based execution, adaptive runtime intelligence, and modular multi-agent processing.

Current Version: **V7.9.0 Release Candidate**

## Overview

AI Summarizer has evolved from a simple text summarization application into a modular execution platform capable of coordinating multiple AI agents through a deterministic execution graph.

The platform emphasizes:

- Graph-based orchestration
- Adaptive runtime intelligence
- Deterministic execution
- Runtime observability
- Diagnostics and reporting
- Production-oriented architecture

The current implementation is designed to provide a stable execution runtime while remaining extensible for future distributed and enterprise deployments.

## Key Features

### Multi-Agent Execution

Supported processing capabilities include:

- Summary
- Actions
- Insights
- Findings
- Sentiment
- Trend
- Risk
- Root Cause
- Forecast
- Recommendation

### Graph-Based Orchestration

- Immutable execution graph
- Dependency validation
- Layer-based scheduling
- Parallel execution support

### Adaptive Runtime

- Runtime reasoning
- Strategy selection
- Decision engine
- Runtime lifecycle management

### Runtime Operations

- Observability
- Diagnostics
- Reporting
- Event-driven execution
- Middleware pipeline

## Architecture Overview

```text
API

↓

Runtime Manager

↓

Runtime Session

↓

Runtime Context

↓

Runtime Intelligence

↓

Scheduler

↓

Execution Engine

↓

Layer Executor

↓

Node Executor

↓

Agents

↓

Observability

↓

Diagnostics

↓

Reporting
```

For detailed architecture documentation, see `ARCHITECTURE.md`.

## Repository Structure

```text
app/
├── agents/
├── orchestration/
│   ├── execution/
│   ├── graph/
│   ├── registry/
│   └── scheduler/
├── runtime/
│   ├── intelligence/
│   ├── observability/
│   ├── diagnostics/
│   ├── reporting/
│   ├── events/
│   ├── middleware/
│   └── ...
├── routes/
├── services/
└── tests/
```

## Quick Start

### Clone

```bash
git clone <repository-url>
cd ai-summarizer
```

### Create Virtual Environment

```bash
python -m venv venv311
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the Application

```bash
uvicorn app.main:app --reload
```

## Running Tests

Run the complete validation suite:

```bash
pytest
```

Formatting:

```bash
black .
```

Static analysis:

```bash
ruff check .
```

Pre-commit validation:

```bash
pre-commit run --all-files
```

## Documentation

Project documentation is organized as follows:

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview and getting started |
| `ARCHITECTURE.md` | Technical architecture |
| `CHANGELOG.md` | Release history |
| `PROJECT_STATUS.md` | Current development status |
| `ROADMAP.md` | Future direction |

## Current Status

Version:

**V7.9.0 Release Candidate**

Project State:

- Feature Complete
- Runtime Platform Stable
- Documentation Synchronized
- Release Candidate Validation

Automated Validation:

- Black
- Ruff
- Pytest
- Pre-commit

Current automated test count:

**237 passing tests**

## Roadmap

### Completed

- Agent architecture
- Graph execution
- Runtime platform
- Adaptive runtime intelligence
- Observability
- Diagnostics
- Reporting

### Planned

- Distributed runtime execution
- Enterprise observability
- Persistent execution history
- Multi-runtime orchestration

## Contributing

Contributions should maintain the project's architectural principles:

- Deterministic execution
- Strong component isolation
- Comprehensive automated testing
- Production-oriented design

Before submitting changes, ensure:

```bash
black .
ruff check .
pytest
pre-commit run --all-files
```

## License

Add the appropriate license information for this repository.

# V8.0.0
# AI Summarizer — Distributed Agent Runtime Platform
## Architecture overview
AI Summarizer V8.0.0 is an Agentic AI Workflow Engine designed for enterprise-grade distributed document processing
. The system has evolved from a deterministic DAG engine (V7.7) into a fully managed distributed platform where specialized AI agents execute across a cluster of workers coordinated by a centralized runtime

## Installation
Environment: Requires Python 3.11+

## Configuration
Pre-commit Hooks:
Configuration
Configuration is managed via a .env file at the root.
Provider Selection: Set AI_PROVIDER to openai, ollama, or fake

API Keys: Configure OPENAI_API_KEY for live model access

Runtime settings: Customize MAX_WORKERS and RETRY_COUNT in RuntimeConfig

## FastAPI endpoints
POST /api/v1/summarize: Main entry point for AI-powered document summarization

GET /metrics: Prometheus-compatible endpoint for real-time monitoring

GET /history: View historical execution results and metadata

POST /playground/execute: Debugging endpoint for inspecting execution graphs and traces

## AI Provider support
The platform features a provider-neutral abstraction layer
 Current support includes:
OpenAI: Standard API and Azure OpenAI compatibility

Local Models: Integration with Ollama and other local inference servers

Mock Provider: Deterministic testing for CI/CD environments

## Metrics endpoint
The /metrics endpoint exposes live operational telemetry including queue depth, active worker counts, and per-agent execution latency, fully integrated with a Prometheus Metrics Exporter

## Plugin system
The Plugin SDK allows third-party developers to extend the platform with new agents, tools, and execution strategies without modifying the core runtime
 It handles dynamic discovery, lifecycle management, and version compatibility

## Memory subsystem
Features a sophisticated multi-layered memory architecture

Scoped Memory: Namespaces for global, tenant, and per-execution state.
Vector Store: Abstracted interface for semantic search and RAG pipelines

Retrieval Pipeline: Context-aware retrieval building for agent prompting

## Worker runtime
The worker is the atomic execution node. It hosts a full V7.9 runtime instance, receiving tasks from a central queue and reporting heartbeat and health metrics to the coordinator

## Development workflow
The project follows a strict RFC-driven engineering process

1. Architecture Review: Impact audit and interface specification.
2. Implementation: Complete, production-ready code with strong typing.
3. Testing: Mandatory unit and regression tests (Pytest).
4. Integration: Validation against the frozen V7.7 execution kernel.