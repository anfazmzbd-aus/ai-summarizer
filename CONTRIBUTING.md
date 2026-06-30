# Contributing Guide

## Objective

Maintain deterministic execution guarantees.

---

## Development Flow

Create branch:

feature/<name>

Examples:

feature/v7.8-observability
feature/retry-snapshots

Never commit directly to main.

---

## Before Opening PR

Required:

pytest

Optional:

pytest --cov=app

Verify:

uvicorn app.main:app --reload

---

## Architecture Rules

Do:

* extend ExecutionGraph
* add contracts
* preserve immutable state

Do Not:

* add execution_order
* mutate graph during runtime
* bypass contracts

---

## PR Checklist

[ ] tests pass

[ ] imports stable

[ ] contracts updated

[ ] docs updated

[ ] ADR required if architecture changed
