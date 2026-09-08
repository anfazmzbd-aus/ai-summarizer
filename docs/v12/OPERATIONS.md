# AI Summarizer V12 — Operations Guide

## 1. Purpose

This document defines the supported operational procedures for AI Summarizer V12.

It covers:

* runtime startup,
* configuration verification,
* application validation,
* supported product interfaces,
* representative operational checks,
* shutdown,
* runtime-state expectations,
* provider-operation guidance,
* operational security considerations.

This guide describes the standalone production operating model certified during V12.

---

## 2. Certified Runtime Model

AI Summarizer V12 is operated as a FastAPI application served by Uvicorn.

Certified application entry point:

```text
app.main:app
```

Certified production startup command:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The development option:

```text
--reload
```

is not part of the certified production startup contract.

---

## 3. Runtime Prerequisites

Before starting the application, verify:

```text
Python 3.11 active
Virtual environment activated
Runtime dependencies installed
Required environment variables configured
Configured port available
```

Recommended verification:

```powershell
python --version
```

Expected:

```text
Python 3.11.x
```

To verify Uvicorn is available:

```powershell
uvicorn --version
```

If runtime dependencies are missing, reinstall them with:

```powershell
pip install -r requirements.txt
```

---

## 4. Initial Offline Operation

For first startup and operational validation, use the deterministic `fake` provider.

PowerShell:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

Start:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Expected startup includes messages equivalent to:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

The exact process identifier and logging format may vary.

---

## 5. Production Startup

From the extracted standalone release directory with the Python 3.11 virtual environment activated:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The certified bind address:

```text
127.0.0.1
```

limits the listener to the local host.

Any decision to expose the service externally through a reverse proxy, network listener, container, service manager, or infrastructure platform is deployment-environment specific and is outside the standalone V12 certification boundary unless separately validated.

---

## 6. Validate Application Startup

After startup, use a separate PowerShell session.

### Validate root application

```powershell
Invoke-WebRequest `
    http://127.0.0.1:8000/ `
    -UseBasicParsing
```

Expected:

```text
HTTP 200
```

### Validate API documentation

```powershell
Invoke-WebRequest `
    http://127.0.0.1:8000/docs `
    -UseBasicParsing
```

Expected:

```text
HTTP 200
```

A successful response from both endpoints confirms that:

* the FastAPI application loaded,
* Uvicorn is accepting requests,
* the web application route is available,
* the API documentation route is available.

---

## 7. Validate the Canonical Summarization Path

Create a representative request:

```powershell
$body = @{
    text = "Operational validation confirms that the standalone AI Summarizer application is functioning."
    provider = "fake"
    model = "demo"
} | ConvertTo-Json
```

Submit:

```powershell
Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/api/v1/summarize `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

A successful response should contain a summary and associated execution information such as:

```text
summary
model
prompt_tokens
completion_tokens
total_tokens
metadata
```

This test exercises the canonical product path through the public API and the configured provider boundary.

---

## 8. Web Interface Operation

Open:

```text
http://127.0.0.1:8000/
```

The user can submit supported text for summarization through the browser interface.

Successful operation confirms:

```text
Browser/UI
    ↓
Public application boundary
    ↓
Summarization application
    ↓
Summarization pipeline
    ↓
Configured provider
    ↓
Product response
```

The canonical V11/V12 product flow must not be bypassed by operational procedures.

---

## 9. API Operation

The canonical summarization API endpoint is:

```text
POST /api/v1/summarize
```

Representative request:

```json
{
  "text": "Text to summarize.",
  "provider": "fake",
  "model": "demo"
}
```

The `text` value must contain non-whitespace content.

Blank or whitespace-only input is rejected by the public product boundary.

Internal application controls that are not part of the public request contract must not be relied upon by external operators.

---

## 10. Provider Modes

### `fake`

Use:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

Recommended for:

* initial installation verification,
* operational smoke tests,
* deterministic demonstrations,
* diagnosis of local application issues,
* isolation of external-provider problems.

No OpenAI API credential is required.

### `openai`

Use:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-api-key>"
$env:OPENAI_MODEL = "<supported-model>"
```

Optional:

```powershell
$env:OPENAI_BASE_URL = "<optional-compatible-endpoint>"
$env:OPENAI_ORGANIZATION = "<optional-organization>"
```

Live-provider operation introduces dependencies outside the local application, including:

* network connectivity,
* credential validity,
* provider availability,
* account permissions,
* selected model availability,
* provider quotas or usage restrictions.

When diagnosing a live-provider problem, first confirm that the same application installation operates correctly with `AI_PROVIDER=fake`.

---

## 11. OpenRouter Operation

OpenRouter may be used through the certified OpenAI-compatible provider path.

Example:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-openrouter-api-key>"
$env:OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
$env:OPENAI_MODEL = "<openrouter-model-identifier>"
```

OpenRouter is not configured as:

```text
AI_PROVIDER=openrouter
```

in the certified V12 product configuration.

It operates through:

```text
AI_PROVIDER=openai
```

with an OpenAI-compatible base URL.

---

## 12. Configuration Inspection

Inspect non-sensitive runtime configuration:

```powershell
$env:AI_PROVIDER
$env:OPENAI_MODEL
$env:OPENAI_BASE_URL
$env:OPENAI_ORGANIZATION
```

Do not routinely print API credentials.

To confirm whether the API key exists without displaying it:

```powershell
if ($env:OPENAI_API_KEY) {
    "OPENAI_API_KEY is configured"
} else {
    "OPENAI_API_KEY is not configured"
}
```

---

## 13. Runtime Logs and Diagnostics

Normal startup and request information is emitted through the application's configured runtime/logging behavior and the Uvicorn process.

Operators should retain the following diagnostic information when investigating failures:

```text
Timestamp
Startup command
Python version
AI_PROVIDER
OPENAI_MODEL
Whether OPENAI_API_KEY is configured
HTTP status
Request endpoint
Error classification/message
Relevant Uvicorn/application log output
```

Do not include:

```text
API keys
authentication tokens
sensitive request data
private credentials
```

in issue reports or shared diagnostic output.

The release artifact does not rely on a pre-existing runtime log file or database from the development repository.

---

## 14. Normal Operational Validation Sequence

A recommended operational validation sequence is:

```text
1. Activate Python 3.11 environment
2. Verify configuration
3. Start application
4. Verify GET /
5. Verify GET /docs
6. Execute POST /api/v1/summarize
7. Confirm successful response
8. Review runtime output for unexpected failures
```

For fault isolation, perform this sequence first with:

```text
AI_PROVIDER=fake
OPENAI_MODEL=demo
```

before testing an external provider.

---

## 15. Application Shutdown

For an interactive Uvicorn process, stop the service using:

```text
Ctrl+C
```

Expected behavior:

```text
Shutdown initiated
Application process terminates
Listener on configured port closes
```

After shutdown, requests to the previous listener should no longer succeed.

---

## 16. Verify Port Release

After shutdown, you may verify whether port `8000` remains in use:

```powershell
Get-NetTCPConnection `
    -LocalPort 8000 `
    -ErrorAction SilentlyContinue
```

If no other process is using the port, no active application listener should remain.

---

## 17. Restart Procedure

A normal restart is:

```text
Stop application
    ↓
Confirm process terminated
    ↓
Apply required environment-variable changes
    ↓
Start application
    ↓
Repeat operational validation
```

Environment-variable changes made in another PowerShell process do not automatically modify an already running Uvicorn process.

Restart after changing provider configuration.

---

## 18. Changing Provider Configuration

To change from offline operation to OpenAI:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-api-key>"
$env:OPENAI_MODEL = "<supported-model>"
```

Restart the application after changing configuration.

To return to deterministic offline operation:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_ORGANIZATION -ErrorAction SilentlyContinue
```

The API key may also be removed from the current session when it is no longer required:

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
```

---

## 19. Operational Security

Operators must:

* protect API credentials,
* avoid exposing credentials in command history where inappropriate,
* avoid committing secrets to Git,
* avoid including secrets in release files,
* avoid logging or sharing credentials,
* use appropriate host/service account permissions,
* verify release checksums before installation,
* use trusted dependency and provider endpoints.

The application is designed to suppress provider credentials from normal configuration representation and product-safe provider failure responses.

---

## 20. Release Artifact Hygiene

The standalone release is intentionally independent of local development state.

Operators must not add dependencies on:

```text
.git/
.env
venv311/
development caches
IDE state
runtime databases from development
runtime logs from development
historical ZIP files
developer-specific paths
```

Persistent deployment-specific runtime state, if introduced by the surrounding deployment environment, must be managed independently from the certified release artifact.

---

## 21. Production Validation Checklist

Before considering an installation operational, confirm:

```text
[ ] Python 3.11 active
[ ] Runtime dependencies installed
[ ] Provider configuration valid
[ ] Application starts without --reload
[ ] GET / returns HTTP 200
[ ] GET /docs returns HTTP 200
[ ] POST /api/v1/summarize succeeds
[ ] No credential appears in normal output
[ ] Application can be stopped cleanly
```

For a live provider:

```text
[ ] External network access available
[ ] API credential configured
[ ] Model identifier valid
[ ] Optional base URL valid when used
[ ] Provider request succeeds
```

---

## 22. Operational Failure Handling

If any mandatory startup or validation step fails:

1. stop the application if it is partially running,
2. record the observed error without exposing secrets,
3. validate Python and dependency state,
4. switch to the deterministic `fake` provider,
5. repeat startup and summarization validation,
6. consult:

```text
docs/v12/TROUBLESHOOTING.md
```

If `fake` operation succeeds but live operation fails, investigate provider configuration, connectivity, credentials, account state, endpoint, or model availability before modifying application source.

---

## 23. Related Documentation

```text
Installation:
docs/v12/INSTALLATION.md

Configuration:
docs/v12/CONFIGURATION.md

Troubleshooting:
docs/v12/TROUBLESHOOTING.md

Release information:
docs/v12/RELEASE_NOTES.md
```
