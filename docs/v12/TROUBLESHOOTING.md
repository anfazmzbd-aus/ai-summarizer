# AI Summarizer V12 — Troubleshooting Guide

## 1. Purpose

This guide provides supported diagnostic procedures for common AI Summarizer V12 installation, startup, configuration, provider, request, and shutdown failures.

The objective is to distinguish:

```text
installation problem
runtime problem
configuration problem
request problem
external-provider problem
```

without changing the certified application architecture.

Do not modify source code as the first response to an operational failure.

---

## 2. Primary Diagnostic Principle

When a live-provider operation fails, first determine whether the standalone application itself is healthy.

Use:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

then start:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

and execute a representative request.

If `fake` operation succeeds but `openai` operation fails, the problem is likely associated with:

* external connectivity,
* credentials,
* endpoint configuration,
* account permissions,
* model availability,
* external provider availability.

This avoids incorrectly treating an external-provider failure as an application defect.

---

## 3. Python Version Problems

### Symptom

The virtual environment was created with an unsupported or unintended Python version.

Example:

```text
Python 3.14.x
```

### Diagnosis

Run:

```powershell
python --version
```

and:

```powershell
py -0p
```

### Resolution

Create a new environment explicitly with Python 3.11:

```powershell
deactivate
```

Remove the incorrect environment if appropriate, then:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

Expected:

```text
Python 3.11.x
```

Reinstall dependencies:

```powershell
pip install -r requirements.txt
```

---

## 4. Virtual Environment Will Not Activate

### Symptom

PowerShell rejects:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Checks

Verify the environment exists:

```powershell
Test-Path .\.venv\Scripts\Activate.ps1
```

Expected:

```text
True
```

If it does not exist, recreate the environment:

```powershell
py -3.11 -m venv .venv
```

PowerShell execution-policy configuration is system-specific. Do not weaken organizational security controls solely to run the application. Use an approved execution-policy or shell approach for the target environment.

---

## 5. Dependency Installation Failure

### Symptom

```powershell
pip install -r requirements.txt
```

fails.

### Checks

Confirm:

```powershell
python --version
python -m pip --version
```

Verify that:

```text
Python == 3.11.x
pip belongs to the active .venv
requirements.txt exists
```

Upgrade pip inside the active environment:

```powershell
python -m pip install --upgrade pip
```

Retry:

```powershell
python -m pip install -r requirements.txt
```

Network or package-index failures must be resolved at the host/environment level.

Do not modify `requirements.txt` merely to bypass a temporary dependency-download failure.

---

## 6. `uvicorn` Command Not Found

### Symptom

PowerShell reports that `uvicorn` is not recognized.

### Diagnosis

Run:

```powershell
python -m pip show uvicorn
```

If Uvicorn is absent, runtime dependencies may not have been installed into the active environment.

### Resolution

Confirm the virtual environment is active and run:

```powershell
python -m pip install -r requirements.txt
```

Then retry:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## 7. Application Import Failure

### Symptom

Startup reports an error importing:

```text
app.main
```

or:

```text
app.main:app
```

### Diagnosis

Confirm you are running the command from the extracted AI Summarizer release root.

Check:

```powershell
Test-Path .\app\main.py
Test-Path .\requirements.txt
```

Both should normally return:

```text
True
```

### Resolution

Change to the correct extracted release directory and retry.

Do not start the application from an unrelated working directory that cannot resolve the `app` package.

---

## 8. Port 8000 Already in Use

### Symptom

Uvicorn reports an address-binding error.

### Diagnosis

Run:

```powershell
Get-NetTCPConnection `
    -LocalPort 8000 `
    -ErrorAction SilentlyContinue
```

If a listener exists, identify the owning process:

```powershell
Get-NetTCPConnection `
    -LocalPort 8000 `
    -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort, State, OwningProcess
```

Then:

```powershell
Get-Process -Id <OwningProcess>
```

### Resolution

Stop the conflicting process if it is safe and authorized to do so.

Alternatively, for local diagnostic operation, use another port:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Use the matching port in validation requests.

---

## 9. Root Page Does Not Respond

### Symptom

```text
GET /
```

fails.

### Checks

Confirm the Uvicorn process is still running.

Verify the configured address and port.

Test:

```powershell
Invoke-WebRequest `
    http://127.0.0.1:8000/ `
    -UseBasicParsing
```

If `/docs` also fails, investigate application startup or listener configuration rather than the summarization pipeline.

---

## 10. `/docs` Does Not Respond

### Symptom

```text
GET /docs
```

fails.

### Checks

Verify:

```powershell
Invoke-WebRequest `
    http://127.0.0.1:8000/ `
    -UseBasicParsing
```

If `/` and `/docs` both fail, investigate startup/listener issues.

If `/` succeeds but `/docs` fails, capture the HTTP status and application output for further diagnosis.

---

## 11. Blank Text Is Rejected

### Symptom

A summarization request returns HTTP `422`.

Example invalid input:

```json
{
  "text": "   ",
  "provider": "fake",
  "model": "demo"
}
```

### Explanation

This is expected V12 behavior.

The public request boundary rejects empty and whitespace-only text.

### Resolution

Submit non-empty text:

```json
{
  "text": "Text to summarize.",
  "provider": "fake",
  "model": "demo"
}
```

Do not disable or weaken the validation rule.

---

## 12. Unsupported Provider

### Symptom

The configured provider is rejected.

Examples of unsupported V12 provider values include:

```text
mock
openrouter
```

when supplied directly as `AI_PROVIDER`.

### Supported values

```text
fake
openai
```

### Resolution

For offline operation:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

For OpenAI:

```powershell
$env:AI_PROVIDER = "openai"
```

For OpenRouter, continue using the certified `openai` provider boundary and configure:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
```

Do not set:

```text
AI_PROVIDER=openrouter
```

for the certified V12 runtime.

---

## 13. Missing OpenAI API Key

### Symptom

Live OpenAI-provider configuration fails at startup or request execution because no credential is configured.

### Diagnosis

Check whether the variable exists without printing it:

```powershell
if ($env:OPENAI_API_KEY) {
    "OPENAI_API_KEY is configured"
} else {
    "OPENAI_API_KEY is not configured"
}
```

### Resolution

Configure the credential:

```powershell
$env:OPENAI_API_KEY = "<your-api-key>"
```

Then restart the application.

The application is expected to fail closed when an OpenAI provider requires a key and none is supplied.

Do not modify the application to bypass this credential requirement.

---

## 14. OpenAI Request Fails

### Symptom

Offline `fake` requests work but live OpenAI requests fail.

### Diagnostic sequence

First verify:

```text
AI_PROVIDER=openai
OPENAI_API_KEY configured
OPENAI_MODEL configured
```

Then inspect optional values:

```powershell
$env:OPENAI_BASE_URL
$env:OPENAI_ORGANIZATION
```

Possible causes include:

* invalid API key,
* unavailable model,
* incorrect base URL,
* account restriction,
* quota or provider-side limit,
* network failure,
* external provider outage.

### Isolation test

Switch temporarily to:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

Restart and retest.

If `fake` succeeds, the canonical local application path is functioning and the problem should be investigated at the external-provider boundary.

---

## 15. OpenRouter Request Fails

### Confirm configuration

Use:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-openrouter-api-key>"
$env:OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
$env:OPENAI_MODEL = "<openrouter-model-identifier>"
```

Do not use:

```text
AI_PROVIDER=openrouter
```

### Common causes

* invalid OpenRouter key,
* incorrect model identifier,
* model unavailable to the account,
* incorrect compatible endpoint,
* provider-side quota or routing failure,
* external network failure.

Return to `fake` mode to confirm local application health before changing source code.

---

## 16. Provider Error Returns HTTP 500

### Symptom

A live-provider failure produces a server error.

### Expected security behavior

The product-facing error must not expose:

* API keys,
* credentials,
* provider secrets,
* internal sensitive diagnostic data.

Record:

```text
HTTP status
timestamp
provider type
model
safe returned error text
relevant server log output
```

Do not paste credentials into diagnostic tickets or reports.

---

## 17. Model Is Not Available

### Symptom

The external provider rejects the configured model.

### Diagnosis

Check:

```powershell
$env:OPENAI_MODEL
```

### Resolution

Configure a model identifier available to the selected external provider/account:

```powershell
$env:OPENAI_MODEL = "<supported-model>"
```

Restart the application.

Model availability is controlled externally and is not guaranteed by AI Summarizer.

---

## 18. Wrong Base URL

### Symptom

External-provider calls fail after setting:

```text
OPENAI_BASE_URL
```

### Diagnosis

Inspect:

```powershell
$env:OPENAI_BASE_URL
```

For default OpenAI behavior, remove the override:

```powershell
Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue
```

For OpenRouter:

```powershell
$env:OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
```

Restart the application after changing the environment.

---

## 19. Environment Changes Have No Effect

### Symptom

A running application continues to use previous provider configuration.

### Explanation

The Uvicorn process inherits environment variables when it starts.

Changing variables in another shell does not reconfigure the existing process.

### Resolution

Stop the current application:

```text
Ctrl+C
```

Apply configuration changes in the shell that will start the new process.

Then restart:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## 20. `.env` Values Are Ignored

### Symptom

A user creates a project-root `.env` file but runtime configuration does not change.

### Explanation

The canonical V12 application does not require automatic `.env` loading for production startup.

`.env.example` is a configuration reference/template.

### Resolution

Set environment variables through the execution environment.

PowerShell example:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

Use an approved service, shell, deployment, or secrets-management mechanism for persistent production configuration.

---

## 21. Request Works in Swagger but Not PowerShell

### Checks

Verify:

```text
URI
HTTP method
Content-Type
JSON body
port number
```

Example known-good PowerShell request:

```powershell
$body = @{
    text = "PowerShell API troubleshooting request."
    provider = "fake"
    model = "demo"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/api/v1/summarize `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

If using port `8001`, update the URI accordingly.

---

## 22. Request Works with `fake` but Not Live Provider

This is an important diagnostic result.

It indicates that these local components are operational:

```text
FastAPI application
public request boundary
canonical application path
summarization pipeline
response construction
local runtime
```

Investigate:

```text
credentials
network
provider endpoint
model
external account state
provider availability
```

before considering application changes.

---

## 23. Application Does Not Stop

### Normal shutdown

Use:

```text
Ctrl+C
```

Allow the Uvicorn process to terminate.

### Verify listener

```powershell
Get-NetTCPConnection `
    -LocalPort 8000 `
    -ErrorAction SilentlyContinue
```

If a process remains, identify it before taking further action:

```powershell
Get-NetTCPConnection `
    -LocalPort 8000 `
    -ErrorAction SilentlyContinue |
    Select-Object OwningProcess
```

Do not terminate unrelated processes.

---

## 24. Standalone Installation Works Only in the Development Repository

### Symptom

The application works from:

```text
E:\Projects\ai-summarizer
```

but not from the extracted release.

### Classification

This is potentially a serious standalone-release defect.

V12 must not depend on:

* the original repository path,
* `venv311`,
* untracked files,
* local databases,
* hidden configuration,
* IDE state,
* historical development artifacts.

### Action

Reproduce the failure from a clean extracted release and record:

```text
artifact name
artifact checksum
Python version
installation commands
configuration
startup command
observed error
```

Do not copy arbitrary development files into the release as a workaround.

Such a dependency may affect CERT-CLEAN or CERT-PKG and must be investigated through V12 release governance.

---

## 25. Release Checksum Does Not Match

### Symptom

The calculated SHA-256 differs from the distributed checksum.

### Action

Do not install or operate that artifact as the certified release.

Re-acquire the release artifact from the trusted distribution source.

A checksum mismatch may indicate:

* corruption,
* incomplete transfer,
* wrong artifact version,
* unauthorized modification,
* source/artifact identity failure.

Release-artifact integrity failures are certification concerns and must not be ignored.

---

## 26. Unexpected Secret Appears in Logs or Error Output

### Action

Do not share the output further.

Record only the minimum non-secret details needed to reproduce the issue.

A confirmed production secret-disclosure defect is a security finding and must be handled under V12 release-blocker governance.

Do not work around it by documenting that operators should ignore exposed credentials.

---

## 27. Diagnostic Information to Collect

For a reproducible support report, collect:

```text
Release/milestone version
Artifact filename
Python version
Operating system
Startup command
AI_PROVIDER
OPENAI_MODEL
Whether OPENAI_API_KEY is configured
OPENAI_BASE_URL if non-sensitive
Endpoint requested
HTTP status
Safe error text
Relevant application/Uvicorn logs
Steps to reproduce
Whether fake provider succeeds
```

Do not collect or publish the API-key value.

---

## 28. When Not to Change Source Code

Do not change source merely because of:

* invalid API credentials,
* incorrect environment variables,
* unavailable models,
* external provider outages,
* port conflicts,
* wrong Python interpreter,
* missing dependency installation,
* incorrect working directory,
* temporary network failures.

V12 source changes require a demonstrated release defect and must remain within the feature-frozen certification scope.

---

## 29. Escalation Criteria

Escalate as a possible V12 release defect when a reproducible failure shows that:

```text
the documented clean installation cannot complete
OR
the application cannot start with certified configuration
OR
the fake provider cannot execute the canonical summarization path
OR
mandatory product endpoints fail in the certified environment
OR
secrets are exposed
OR
the standalone artifact depends on undocumented development state
OR
the release artifact identity cannot be verified
```

A confirmed P0 or P1 defect blocks final `v12.0.0` release until resolved and recertified.

---

## 30. Recovery Baseline

When configuration state is uncertain, return to the known offline baseline.

Stop the application.

Then:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"

Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_ORGANIZATION -ErrorAction SilentlyContinue
```

Restart:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Validate:

```text
GET /
GET /docs
POST /api/v1/summarize
```

If this baseline succeeds, reintroduce external-provider configuration one element at a time.

---

## 31. Related Documentation

```text
Installation:
docs/v12/INSTALLATION.md

Configuration:
docs/v12/CONFIGURATION.md

Operations:
docs/v12/OPERATIONS.md

Release information:
docs/v12/RELEASE_NOTES.md
```
