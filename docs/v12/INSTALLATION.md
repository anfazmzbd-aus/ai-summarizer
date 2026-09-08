# AI Summarizer V12 — Installation Guide

## 1. Purpose

This guide defines the supported standalone installation procedure for AI Summarizer V12.

The procedure is based on the production deployment and clean-install path certified during V12 M4.

The installation must succeed without relying on the original development repository, development virtual environment, IDE configuration, hidden files, or undocumented setup.

---

## 2. Supported Runtime

The certified runtime family is:

```text
Python 3.11
```

V12 clean-install certification was performed with:

```text
Python 3.11.9
```

Python 3.14 is not part of the certified V12 runtime baseline.

---

## 3. Release Artifact

The final V12 standalone distribution format is:

```text
ai-summarizer-v12.0.0.zip
```

Milestone and release-candidate artifacts may use version-qualified names such as:

```text
ai-summarizer-v12.0.0-m4.zip
ai-summarizer-v12.0.0-rc1.zip
```

A SHA-256 checksum file accompanies certified release artifacts.

---

## 4. Installation Prerequisites

Before installation, confirm that the target system provides:

* Python 3.11,
* Python `venv`,
* pip,
* sufficient permission to create files and virtual environments,
* network access only when installing dependencies or using a live provider.

For deterministic `fake` provider operation, no external AI-provider API access is required after dependencies are installed.

---

## 5. Verify Python 3.11

### Windows PowerShell

List installed Python interpreters:

```powershell
py -0p
```

Confirm that Python 3.11 is available.

Verify directly:

```powershell
py -3.11 --version
```

Expected:

```text
Python 3.11.x
```

Do not use a generic:

```powershell
python -m venv .venv
```

unless you have independently confirmed that `python` resolves to Python 3.11.

For V12 certification and clean-install procedures, use:

```powershell
py -3.11 -m venv .venv
```

---

## 6. Verify the Release Checksum

When a checksum file is supplied, verify the ZIP before extraction.

Example:

```powershell
Get-FileHash `
    .\ai-summarizer-v12.0.0.zip `
    -Algorithm SHA256
```

Compare the resulting hash with:

```text
ai-summarizer-v12.0.0.zip.sha256
```

Do not install from an artifact whose checksum does not match the certified checksum.

---

## 7. Extract the Release

Extract the ZIP into a clean directory.

Example:

```text
E:\Applications\ai-summarizer-v12.0.0
```

The extracted package contains a version-rooted directory.

Enter that directory before continuing.

Example:

```powershell
Set-Location E:\Applications\ai-summarizer-v12.0.0
```

Do not copy the development repository's:

* `venv311`,
* `.env`,
* caches,
* databases,
* logs,
* IDE configuration,
* untracked files

into the clean installation.

---

## 8. Create a Clean Virtual Environment

Create the environment explicitly with Python 3.11:

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify the active interpreter:

```powershell
python --version
```

Expected:

```text
Python 3.11.x
```

---

## 9. Upgrade pip

Run:

```powershell
python -m pip install --upgrade pip
```

This updates pip inside the clean virtual environment rather than changing the system Python installation.

---

## 10. Install Runtime Dependencies

Install the runtime requirements from the release:

```powershell
pip install -r requirements.txt
```

The standalone runtime depends on:

```text
requirements.txt
```

Development requirements are not required for normal product operation.

---

## 11. Configure Offline Validation

For the first startup, use the deterministic `fake` provider.

PowerShell:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

No OpenAI API key is required for this mode.

See:

```text
docs/v12/CONFIGURATION.md
```

for live-provider configuration.

---

## 12. Start the Application

Start the application using the certified production command:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Expected startup output includes:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

The development option:

```text
--reload
```

is not required and is not part of the V12 production startup contract.

---

## 13. Validate the Web Application

From a second PowerShell terminal:

```powershell
Invoke-WebRequest `
    http://127.0.0.1:8000/ `
    -UseBasicParsing
```

Expected:

```text
StatusCode : 200
```

You may also open:

```text
http://127.0.0.1:8000/
```

in a browser.

---

## 14. Validate API Documentation

Run:

```powershell
Invoke-WebRequest `
    http://127.0.0.1:8000/docs `
    -UseBasicParsing
```

Expected:

```text
StatusCode : 200
```

Browser URL:

```text
http://127.0.0.1:8000/docs
```

---

## 15. Validate Summarization

Create a representative request:

```powershell
$body = @{
    text = "Clean installation validation confirms that AI Summarizer can run independently from its release artifact."
    provider = "fake"
    model = "demo"
} | ConvertTo-Json
```

Call the canonical endpoint:

```powershell
Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/api/v1/summarize `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

A successful response should contain fields such as:

```text
summary
model
prompt_tokens
completion_tokens
total_tokens
metadata
```

The exact generated summary content is provider-dependent.

---

## 16. Stop the Application

Return to the terminal running Uvicorn and press:

```text
Ctrl+C
```

A normal shutdown should terminate the application cleanly.

---

## 17. Deactivate the Environment

When finished:

```powershell
deactivate
```

---

## 18. Live Provider Installation

No separate installation is required for the `openai` provider beyond the certified runtime dependencies.

Before live-provider startup, configure the required environment variables.

Example:

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

See:

```text
docs/v12/CONFIGURATION.md
```

for configuration and secret-handling requirements.

---

## 19. Installation Success Criteria

The installation is considered successful when all of the following are true:

```text
Python 3.11 active
Dependencies installed successfully
Application starts successfully
GET / returns HTTP 200
GET /docs returns HTTP 200
POST /api/v1/summarize succeeds
Application stops cleanly
```

---

## 20. Prohibited Hidden Dependencies

A valid V12 standalone installation must not require:

* `E:\Projects\ai-summarizer`,
* the original `venv311`,
* the developer's `.env`,
* IDE-specific configuration,
* untracked repository files,
* repository caches,
* historical conversations,
* undocumented environment variables,
* undocumented source changes,
* undocumented manual fixes.

If any such dependency is required, the installation is not compliant with the V12 standalone-release contract.

---

## 21. Next Steps

After installation:

```text
Configuration:
docs/v12/CONFIGURATION.md

Operations:
docs/v12/OPERATIONS.md

Troubleshooting:
docs/v12/TROUBLESHOOTING.md

Release information:
docs/v12/RELEASE_NOTES.md
```
