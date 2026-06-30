# Operations Guide

## Local Run

Start:

uvicorn app.main:app --reload

Open:

/docs

---

## Health Verification

Checklist:

API responds

scheduler builds graph

execution completes

state outputs generated

---

## Recovery

If runtime fails:

1 rollback to tag

v7.7-runtime-stable

2 verify tests

3 inspect execution trace

---

## Deployment Strategy

Environment promotion:

dev
↓

staging
↓

production
