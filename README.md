# AI Summarizer

AI Summarizer is a production-oriented FastAPI application for deterministic and provider-backed text summarization.

The current release program is:

```text
V13.0.0 — Product Experience & Release Certification
Current release identity: 13.0.0
```

V13 preserves the certified canonical architecture established through V11 and production-certified in V12. It adds the practical product experience: summarization controls, approved model selection, TXT/PDF ingestion, result-workspace actions, accessibility hardening, and final V13 release certification.

## Supported Environment

Certified runtime family: Python 3.11. V13 clean-install certification was performed with Python 3.11.9. Python 3.14 is not part of the certified V13 runtime baseline.

## Quick Start

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`. API documentation is available at `http://127.0.0.1:8000/docs`.

## Product Surface

V13 supports paste-text summarization and TXT/PDF file ingestion. Product controls include General, Executive, Key Points, Action Items, Findings, Insights, and Technical summary types; Short, Medium, and Detailed lengths; approved product-model selection; and optional custom instructions.

The result workspace supports copy, UTF-8 TXT download, regenerate using the current source and controls, and collapsible processing details. File extraction never starts summarization automatically. Failed extraction preserves the current source, and failed regeneration/summarization preserves an existing successful result where applicable.

V13 does not add history, accounts/authentication, persistence, DOCX ingestion, OCR, arbitrary provider selection, advanced analytics, or a second summarization pipeline.

## Canonical Architecture

```text
Frontend / product API
  -> canonical SummarizationApplication
  -> bounded intelligence
  -> existing V9 summarization pipeline
  -> runtime/provider boundary
  -> product-safe response + metadata
```

`POST /api/v1/summarize` is the canonical summarization endpoint. File extraction rejoins this same summarization path; it does not create a parallel summarization implementation.

## Supported Providers

Certified `AI_PROVIDER` values are:

```text
fake
openai
```

`fake` is deterministic and intended for offline validation, smoke testing, demonstrations, and release certification.

For live OpenAI-compatible operation:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-api-key>"
$env:OPENAI_MODEL = "<supported-model>"
```

Optional values are `OPENAI_BASE_URL` and `OPENAI_ORGANIZATION`.

OpenRouter is supported as an OpenAI-compatible endpoint configuration, not as a separate provider value:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-openrouter-api-key>"
$env:OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
$env:OPENAI_MODEL = "<openrouter-model-identifier>"
```

Do not configure `AI_PROVIDER=openrouter`. Never commit API keys or other secrets.

See `docs/v13/CONFIGURATION.md` for the complete configuration contract.

## File Ingestion

V13 accepts TXT and PDF uploads up to 10 MiB through the certified extraction boundary. TXT content is decoded as UTF-8 with BOM handling and normalized before use. PDF extraction uses the certified PDF dependency; encrypted PDFs and PDFs without extractable text are rejected. DOCX and OCR are outside V13 scope.

## Production Startup

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`--reload` is a development option and is not part of the certified production startup contract.

## Validation

```powershell
Invoke-WebRequest http://127.0.0.1:8000/ -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8000/docs -UseBasicParsing
```

Expected status: HTTP 200.

Development/certification validation is run from the repository:

```powershell
pytest -m "not live" -q
pre-commit run --all-files
git diff --check
```

Live-provider tests are separately controlled and require explicit opt-in.

## Release Artifact

The V13 standalone distribution is a deterministic versioned source ZIP with a SHA-256 checksum. Release-candidate naming is `ai-summarizer-v13.0.0-rc1.zip`; final naming is `ai-summarizer-v13.0.0.zip`.

The artifact contains runtime source, static assets, runtime dependencies, configuration template, and current V13 release documentation. Development/test state, credentials, caches, runtime databases, IDE state, historical release documentation, and other machine-local material are excluded by the release builder.

## Documentation

Authoritative current documentation is under `docs/v13/`:

- `INSTALLATION.md`
- `CONFIGURATION.md`
- `OPERATIONS.md`
- `TROUBLESHOOTING.md`
- `RELEASE_NOTES.md`
- `M9_CERTIFICATION_RECORD.md`

Historical documentation under `docs/v10/`, `docs/v11/`, and `docs/v12/` remains historical evidence and must not be rewritten as current V13 documentation.

## Current Release Status

M1 through M8 are frozen. M9.1 through M9.8 are complete/certified. M9.9 final `v13.0.0` pre-publication certification is complete.

Application identity is `13.0.0`. Pre-publication validation is complete; final publication remains pending the exact final artifact rebuild, final packaged verification, annotated `v13.0.0` tag, and local/remote release-identity verification.
