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

