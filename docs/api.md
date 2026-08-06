# API Documentation

## Home

GET /

Returns application home page.

---

## Summarize

POST /summarize

Parameters:

* text
* summary_length

Returns:

* Summary
* Actions
* Insights
* Findings
* Execution Plan
* Execution Metadata

---

## History

GET /history

Returns previously processed summaries.

---

## Upload

POST /upload

Document upload endpoint.

V7.7-stable

POST /summarize

POST /playground/execute

GET /runtime

# request examples
    API Health Validation:
    Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/docs

    End-to-End Production Path:
    Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/summarize `
    -Method POST `
    -ContentType "application/json" `
    -Body '{
    "text":"Revenue increased by 22%"
    }'

    Playground Debug Validation:
    Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/playground/execute `
    -Method POST `
    -ContentType "application/json" `
    -Body '{
    "text":"Revenue increased by 22%",
    "mode":"summary",
    "debug":true
    }'

# response examples

    Response body:
    {
    "execution_id": "2cef7a0e-09f7-4318-9708-1425fac16aa5",
    "status": "success",
    "result": {
        "summary": "Revenue increased by 22%",
        "insight": "analysis_complete"
    },
    "node_outputs": {
        "summary": {
        "summary": "Revenue increased by 22%"
        },
        "insights": {
        "insight": "analysis_complete"
        }
    },
    "trace": [],
    "metrics": {},
    "errors": [],
    "metadata": {
        "version": "v7.7",
        "execution_model": "deterministic_dag"
    }
    }

    Regression:
    (venv311) PS E:\Projects\ai-summarizer> pytest
    ======================================================= test session starts ========================================================
    platform win32 -- Python 3.11.9, pytest-9.0.3, pluggy-1.6.0
    rootdir: E:\Projects\ai-summarizer
    configfile: pyproject.toml
    testpaths: app/tests
    plugins: anyio-4.13.0
    collected 6 items

    app\tests\test_api_smoke.py .               [ 16%]
    app\tests\test_execution_trace.py .         [ 33%]
    app\tests\test_full_pipeline.py .           [ 50%]
    app\tests\test_metrics.py .                 [ 66%]
    app\tests\test_registry_integrity.py .      [ 83%]
    app\tests\test_runtime_integrity.py .       [100%]

    ======================================================== 6 passed in 0.46s =========================================================


# error responses

====================
## V8.0.0

POST /api/v1/summarize

GET /metrics

GET /docs

GET /openapi.json
