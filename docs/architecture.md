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