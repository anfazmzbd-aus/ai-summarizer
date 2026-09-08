# AI Summarizer V12 — Configuration Guide

## 1. Purpose

This document defines the certified production configuration surface for AI Summarizer V12.

It describes supported provider selection, model configuration, credentials, optional endpoint settings, environment-variable behavior, and secret-handling requirements.

---

## 2. Certified Configuration Surface

The V12 runtime recognizes the following production configuration variables:

```text
AI_PROVIDER
OPENAI_API_KEY
OPENAI_MODEL
OPENAI_BASE_URL
OPENAI_ORGANIZATION
```

These variables form the supported application configuration boundary for the V12 standalone release.

---

## 3. Supported Providers

The certified product configuration supports:

```text
fake
openai
```

Other historical provider names found in older project documentation are not part of the V12 certified product configuration contract unless subsequently certified through the V12 release process.

---

## 4. `AI_PROVIDER`

`AI_PROVIDER` selects the provider implementation used by the canonical application.

Supported values:

```text
fake
openai
```

### Offline example

```powershell
$env:AI_PROVIDER = "fake"
```

### Live example

```powershell
$env:AI_PROVIDER = "openai"
```

Unsupported provider values fail closed rather than silently selecting another provider.

---

## 5. `OPENAI_MODEL`

`OPENAI_MODEL` selects the model identifier supplied to the configured provider.

Offline certification example:

```powershell
$env:OPENAI_MODEL = "demo"
```

The release template currently provides:

```text
OPENAI_MODEL=gpt-5-mini
```

as an example/default model configuration.

For live operation, select a model that is available to the configured provider endpoint and account.

Example:

```powershell
$env:OPENAI_MODEL = "<supported-model>"
```

Model availability is controlled by the external provider and is not guaranteed by the AI Summarizer application.

---

## 6. `OPENAI_API_KEY`

`OPENAI_API_KEY` is required for normal authenticated `openai` provider operation.

Example:

```powershell
$env:OPENAI_API_KEY = "<your-api-key>"
```

A blank or missing API key causes the OpenAI provider configuration to fail closed rather than continuing with an invalid credential state.

`OPENAI_API_KEY` is not required when:

```text
AI_PROVIDER=fake
```

---

## 7. `OPENAI_BASE_URL`

`OPENAI_BASE_URL` is optional.

It allows the OpenAI provider configuration to target an explicitly configured compatible endpoint instead of the provider's default endpoint.

Example:

```powershell
$env:OPENAI_BASE_URL = "<compatible-endpoint>"
```

Leave it unset or empty when the default provider endpoint should be used.

This configuration option does not imply that arbitrary historical providers are independently certified V12 product providers. The certified product boundary remains:

```text
fake
openai
```

### OpenRouter Configuration

OpenRouter may be used through its OpenAI-compatible API endpoint without introducing a separate V12 provider type.

Example:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-openrouter-api-key>"
$env:OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
$env:OPENAI_MODEL = "<openrouter-model-identifier>"
```

In this configuration:

```text
AI_PROVIDER        = openai
OPENAI_API_KEY     = OpenRouter credential
OPENAI_BASE_URL    = https://openrouter.ai/api/v1
OPENAI_MODEL       = model identifier available through OpenRouter
```

The application continues to execute through the certified V12 `openai` provider boundary.

`openrouter` is not a certified standalone value for `AI_PROVIDER` in V12.

---

## 8. `OPENAI_ORGANIZATION`

`OPENAI_ORGANIZATION` is optional.

Example:

```powershell
$env:OPENAI_ORGANIZATION = "<organization-id>"
```

Leave it unset when the provider account does not require organization selection.

---

## 9. Offline Configuration

The recommended initial configuration is:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

This configuration:

* requires no external AI-provider credentials,
* is deterministic,
* supports installation validation,
* supports operational smoke testing,
* is the preferred initial clean-install configuration.

---

## 10. Live OpenAI Configuration

Example:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<your-api-key>"
$env:OPENAI_MODEL = "<supported-model>"
```

Optional endpoint and organization values:

```powershell
$env:OPENAI_BASE_URL = "<optional-compatible-endpoint>"
$env:OPENAI_ORGANIZATION = "<optional-organization>"
```

Start the application after configuration:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## 11. `.env.example`

The release includes:

```text
.env.example
```

with the configuration shape:

```text
AI_PROVIDER=fake

OPENAI_API_KEY=

OPENAI_MODEL=gpt-5-mini

OPENAI_BASE_URL=

OPENAI_ORGANIZATION=
```

This file is a configuration template and reference.

It does not mean that the canonical application automatically loads a project-root `.env` file during production startup.

For standalone operation, provide environment variables using an appropriate mechanism for the deployment environment.

Examples include:

* PowerShell environment variables,
* shell environment variables,
* service/process-manager environment configuration,
* container/orchestration environment injection if externally adopted,
* secure secrets-management systems.

---

## 12. PowerShell Session Configuration

PowerShell environment variables can be set for the active process/session using:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

These values apply to processes launched from that PowerShell environment.

They are not automatically permanent system configuration.

---

## 13. Inspect Current Configuration

PowerShell:

```powershell
$env:AI_PROVIDER
$env:OPENAI_MODEL
$env:OPENAI_BASE_URL
$env:OPENAI_ORGANIZATION
```

Avoid displaying `OPENAI_API_KEY` during routine operational diagnostics.

If credential existence needs to be checked, prefer checking whether it is set rather than printing the secret value.

Example:

```powershell
if ($env:OPENAI_API_KEY) {
    "OPENAI_API_KEY is configured"
} else {
    "OPENAI_API_KEY is not configured"
}
```

---

## 14. Clear Configuration

To remove session-scoped PowerShell values:

```powershell
Remove-Item Env:AI_PROVIDER -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_ORGANIZATION -ErrorAction SilentlyContinue
```

---

## 15. Secret Handling

API credentials are secrets.

Do not:

* commit API keys to Git,
* place live credentials in `README.md`,
* put live secrets into `.env.example`,
* include credentials in release ZIP files,
* paste API keys into issue reports,
* include secrets in screenshots,
* print secrets during diagnostics,
* store credentials in source files.

The V12 release packaging process excludes local `.env` state from the distributable artifact.

The application configuration also suppresses API-key disclosure from normal settings representation.

---

## 16. Provider Failure Behavior

The V12 application is designed to fail closed for invalid provider configuration.

Examples include:

```text
unsupported AI_PROVIDER
missing required OpenAI API key
invalid provider initialization
external provider failure
```

Provider failures must not cause application responses to expose configured secrets.

Detailed operational troubleshooting is provided in:

```text
docs/v12/TROUBLESHOOTING.md
```

---

## 17. Request Provider and Model Fields

The canonical summarization API supports provider and model request fields.

Example:

```json
{
  "text": "Text to summarize.",
  "provider": "fake",
  "model": "demo"
}
```

The application's supported provider boundary remains constrained by the certified runtime provider configuration.

Internal application controls that are not part of the public product request contract must not be supplied through the public API.

---

## 18. Configuration Validation

The simplest configuration validation procedure is:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"

uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then execute:

```powershell
$body = @{
    text = "Configuration validation confirms normal application operation."
    provider = "fake"
    model = "demo"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/api/v1/summarize `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

Successful summarization confirms that the core offline provider configuration is operational.

---

## 19. Configuration Reference

| Variable              | Required for `fake` | Required for `openai` | Purpose                      |
| --------------------- | ------------------: | --------------------: | ---------------------------- |
| `AI_PROVIDER`         |                 Yes |                   Yes | Selects provider             |
| `OPENAI_MODEL`        |                 Yes |                   Yes | Selects provider model       |
| `OPENAI_API_KEY`      |                  No |                   Yes | Provider credential          |
| `OPENAI_BASE_URL`     |                  No |                    No | Optional compatible endpoint |
| `OPENAI_ORGANIZATION` |                  No |                    No | Optional organization        |

---

## 20. Recommended First-Run Configuration

For every new installation, begin with:

```powershell
$env:AI_PROVIDER = "fake"
$env:OPENAI_MODEL = "demo"
```

Validate the local application completely before configuring external provider credentials.

This separates installation/runtime problems from network, credential, account, quota, or provider-service problems.
