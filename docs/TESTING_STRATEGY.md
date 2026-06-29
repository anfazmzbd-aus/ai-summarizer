# Testing Strategy

## Test Pyramid

Unit Tests

graph_builder
graph_validator
state_merger
retry_engine

↓

Integration Tests

execution_engine
scheduler

↓

Pipeline Tests

API
summarization

---

## Required Commands

Run all:

pytest

Run coverage:

pytest --cov=app

Run API:

uvicorn app.main:app --reload

---

## Required Passing Gates

Graph Validation:
100%

Execution Runtime:
100%

Pipeline:
100%

---

## Regression Rule

Every bug fix requires:

1 test reproducing bug
1 passing verification
