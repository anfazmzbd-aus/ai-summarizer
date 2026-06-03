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
