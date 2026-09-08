# AI Summarizer

AI Summarizer is a production-oriented FastAPI application for deterministic and provider-backed text summarization.

The application combines a stable summarization pipeline, bounded intelligence, long-document strategies, provider abstraction, runtime reliability controls, and a web/API product surface.

The current release program is:

```text
V12.0.0 — Production Certification & Standalone Release
```

V12 is feature-frozen. Its purpose is to certify, secure, operationalize, document, package, and release the application architecture completed through V11.

The final `v12.0.0` release is created only after V12 release-candidate and final-release certification complete.

---

## Supported Environment

The certified runtime is:

```text
Python 3.11
```

V12 clean-install certification was performed with:

```text
Python 3.11.9
```

Python 3.14 is not part of the certified V12 runtime baseline.

---

## Quick Start

### Windows PowerShell

Create a clean virtual environment explicitly using Python 3.11:

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify the interpreter:

```powershell
python --version
```

Expected:

```text
Python 3.11.x
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install runtime dependencies:

```powershell
pip install -r requirements.txt
```

Configure deterministic offline operation:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

Start the application:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
Application: http://127.0.0.1:8000/
API documentation: http://127.0.0.1:8000/docs
```

Stop the application with:

```text
Ctrl+C
```

---

## Supported Providers

The certified V12 application configuration supports:

```text
fake
openai
```

### `fake`

`fake` is the deterministic offline provider.

It is suitable for:

* installation validation,
* smoke testing,
* demonstrations,
* local operation without external API access,
* release certification.

Example:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

### `openai`

`openai` enables live OpenAI-compatible provider execution through the application's certified provider boundary.

Example:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-api-key>"
$env:OPENAI_MODEL = "<supported-model>"
```

Optional configuration:

```powershell
$env:OPENAI_BASE_URL = "<optional-compatible-endpoint>"
$env:OPENAI_ORGANIZATION = "<optional-organization>"
```

Never commit real API keys or secrets to source control.

See:

```text
docs/v12/CONFIGURATION.md
```

for the full configuration contract.

---

## Configuration Variables

The certified runtime configuration surface is:

```text
AI_PROVIDER
OPENAI_API_KEY
OPENAI_MODEL
OPENAI_BASE_URL
OPENAI_ORGANIZATION
```

### OpenRouter via the OpenAI-Compatible Endpoint

OpenRouter can be used through the certified `openai` provider path by configuring its OpenAI-compatible API endpoint.

Example:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-openrouter-api-key>"
$env:OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
$env:OPENAI_MODEL = "<openrouter-model-identifier>"
```

OpenRouter is therefore an endpoint configuration of the V12 `openai` provider path rather than a separate `AI_PROVIDER` value.

Do not configure:

```text
AI_PROVIDER=openrouter
```

unless a future certified release explicitly adds that provider value.


The supplied:

```text
.env.example
```

is a configuration reference/template.

The canonical V12 application does not require automatic `.env` loading for production startup. Set environment variables using your operating system, shell, process manager, deployment environment, or another approved secret/configuration mechanism.

---

## Using the Application

### Web interface

Open:

```text
http://127.0.0.1:8000/
```

Enter text and submit it for summarization.

### REST API

Endpoint:

```text
POST /api/v1/summarize
```

Example PowerShell request:

```powershell
$body = @{
    text = "AI Summarizer provides a certified standalone summarization application."
    provider = "fake"
    model = "demo"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/api/v1/summarize `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

A successful response contains the generated summary, model identity, token usage, and canonical execution metadata.

---

## Installation Documentation

For a complete clean-install procedure, see:

```text
docs/v12/INSTALLATION.md
```

The standalone release must not depend on:

* the original development virtual environment,
* developer-specific paths,
* hidden local files,
* IDE configuration,
* undocumented environment variables,
* historical project chat instructions,
* undocumented manual fixes.

---

## Production Startup

The certified V12 production startup command is:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The development reloader:

```text
--reload
```

is intentionally not part of the certified production startup contract.

---

## Validation

After startup, validate the root application:

```powershell
Invoke-WebRequest `
    http://127.0.0.1:8000/ `
    -UseBasicParsing
```

Expected:

```text
HTTP 200
```

Validate API documentation:

```powershell
Invoke-WebRequest `
    http://127.0.0.1:8000/docs `
    -UseBasicParsing
```

Expected:

```text
HTTP 200
```

Then execute a representative summarization request using the `fake` provider.

---

## Testing

Development and certification testing should be performed from the repository rather than from the minimal standalone runtime artifact.

Run the standard non-live regression suite:

```powershell
pytest -m "not live" -q
```

Run quality gates:

```powershell
pre-commit run --all-files
git diff --check
```

Live-provider tests remain separately controlled because they require external credentials and provider access.

---

## Release Artifact

The V12 standalone distribution format is a versioned source ZIP.

Final naming convention:

```text
ai-summarizer-v12.0.0.zip
```

A SHA-256 checksum accompanies the certified distributable artifact.

The release artifact contains the runtime source, required static assets, runtime dependency definition, configuration template, and current V12 release documentation while excluding development/runtime state that is not required by the standalone product.

---

## Release Documentation

Authoritative V12 production documentation is maintained under:

```text
docs/v12/
```

Key documents include:

```text
INSTALLATION.md
CONFIGURATION.md
OPERATIONS.md
TROUBLESHOOTING.md
RELEASE_NOTES.md
```

Certification and governance records in the same directory provide auditable production-readiness evidence.

---

## Architecture and Scope

The canonical application architecture established in V11 is frozen during V12.

V12 does not introduce new:

* summarization architecture,
* provider architecture,
* bounded-intelligence architecture,
* application boundaries,
* orchestration architecture,
* product features,
* UI expansion,
* experimental integrations.

V12 work is limited to production stabilization, security, operational readiness, packaging, documentation, certification, and release integrity.

---

## Current Certification Status

Completed:

```text
M1 — Baseline & Release-Candidate Governance
M2 — Production Stabilization & Regression Certification
M3 — Security & Operational Certification
M4 — Production Deployment & Standalone Packaging
```

Current:

```text
M5 — Documentation & Release Readiness
```

Remaining before final release:

```text
M6 — Release Candidate Certification
M7 — Final V12.0.0 Production Release
```

---

## License

See the repository license file for the applicable project license terms.
