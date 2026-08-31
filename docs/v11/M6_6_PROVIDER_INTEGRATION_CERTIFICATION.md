# V11 M6.6 — Provider Integration & Controlled Real-Provider Validation Certification

## Status

**CERTIFIED**

V11 M6 — Provider Integration & Controlled Real-Provider Validation has completed architecture, integration, live-provider, failure-path, regression, and quality-gate validation.

---

## 1. Scope

M6 validates provider execution through the canonical V11 product architecture while preserving existing V9 provider/runtime ownership and V10 bounded-intelligence authority constraints.

The certified canonical execution path is:

```text
POST /api/v1/summarize
    -> app.routes.ai
    -> SummarizationApplication
    -> app.ai.SummarizationService
    -> AIRuntimeService
    -> LLMClient
    -> AIProviderRegistry
    -> AIProvider
```

Provider selection and runtime behavior remain outside V10 intelligence ownership.

---

## 2. M6.2 — Canonical Provider Integration

Canonical V11 provider integration was validated offline using deterministic `AIProvider` implementations.

Certified behavior includes:

* execution through the real `SummarizationApplication`;
* execution through the real `app.ai.SummarizationService`;
* execution through `AIRuntimeService`;
* execution through `LLMClient`;
* provider resolution through `AIProviderRegistry`;
* deterministic provider selection;
* model propagation;
* prompt-token propagation;
* completion-token propagation;
* total-token aggregation.

Two deterministic provider integration scenarios passed.

---

## 3. M6.3 — Provider Configuration and Error Contracts

Provider configuration behavior was hardened and certified.

### Unknown request provider

An unknown provider requested through the canonical application boundary fails at provider lookup.

The internal provider boundary currently raises `KeyError`.

At the canonical HTTP boundary this is projected as:

```json
{
  "detail": {
    "error": {
      "code": "SUMMARIZATION_FAILED",
      "message": "summarization could not be completed"
    }
  }
}
```

Internal provider names, exception types, and diagnostic details are not exposed.

### Unsupported configured provider

Application composition now fails closed for unsupported configured providers.

Supported canonical configured provider values are:

* `fake`
* `openai`

Unsupported values raise `ValueError` instead of silently falling back to the fake provider.

### OpenAI credential validation

When:

```text
AI_PROVIDER=openai
```

an API key is required before construction of the OpenAI provider.

Missing credentials fail fast at the application composition boundary instead of propagating an SDK credential exception.

### AISettings environment evaluation

`AISettings` environment-backed fields are evaluated when each settings instance is created.

This prevents environment values from being frozen at module-import time and supports isolated runtime/test configuration.

---

## 4. M6.4 — Controlled Real-Provider Validation

A canonical live-provider integration test was added for:

```text
POST /api/v1/summarize
```

The test validates the canonical V11 application path against an OpenAI-compatible live provider.

OpenRouter is used as an OpenAI-compatible transport through the configured OpenAI base URL. The canonical provider identity remains:

```text
openai
```

The live test requires explicit opt-in and an available credential.

Validated states:

```text
normal execution       -> skipped
-m "not live"          -> deselected
--run-live             -> passed
```

The controlled live validation completed successfully with one explicitly initiated live test execution.

No live provider call is required during normal repository validation.

---

## 5. Live-Test Environment Isolation

Legacy live tests previously called `load_dotenv()` during pytest module collection.

Because pytest imports live-test modules before marker deselection, this could mutate the global test-process environment even when live tests were excluded.

This exposed:

```text
AI_PROVIDER=openrouter
```

from `.env` to unrelated canonical API tests.

The live tests were corrected to use non-mutating `.env` reads through `dotenv_values()`.

The resulting contract is:

```text
pytest collection
    -> may read .env values
    -> must not modify os.environ globally
```

Environment mutation required by a live test is scoped to the executing test.

The production fail-closed provider behavior was preserved.

---

## 6. M6.5 — Provider Failure Contracts

Three deterministic offline failure scenarios were certified.

### Provider exception

A provider-generated runtime exception is contained inside the provider/runtime stack.

Canonical API result:

```text
HTTP 500
SUMMARIZATION_FAILED
```

Provider exception details are not exposed.

### Provider timeout

A deterministic slow provider triggers the real `LLMClient` timeout path.

The internal timeout becomes `LLMTimeoutError`.

The canonical product boundary still returns:

```text
HTTP 500
SUMMARIZATION_FAILED
```

Timeout implementation details are not exposed.

### Malformed provider response

A provider returning an invalid response object causes downstream processing to fail safely.

The canonical API returns:

```text
HTTP 500
SUMMARIZATION_FAILED
```

Internal exception types such as `AttributeError` and `NoneType` details are not exposed.

---

## 7. Architecture Certification

Architecture plus M6 regression:

```text
74 passed, 1 deselected
```

This confirms that provider integration did not violate existing architecture guards.

In particular:

* V10 intelligence did not acquire provider ownership;
* V10 intelligence did not acquire runtime ownership;
* V11 continues to execute through the canonical application boundary;
* provider execution remains service/runtime-owned;
* live-provider behavior does not bypass the canonical product path;
* provider failures remain contained behind product-safe API contracts.

---

## 8. Focused M6 Certification

Focused non-live M6 integration validation:

```text
10 passed, 1 deselected
```

Coverage:

```text
M6.2  canonical deterministic provider integration
M6.3  provider/configuration error contracts
M6.4  controlled live-provider validation
M6.5  provider exception/timeout/malformed-response contracts
```

The M6.4 live test is intentionally deselected during non-live execution.

---

## 9. Full Regression Certification

Full repository non-live validation:

```text
3079 passed, 10 deselected
```

All selected tests passed.

The deselected tests are live-test paths intentionally excluded from standard non-live validation.

---

## 10. Quality Gate

The repository quality gate passed:

```text
pre-commit run --all-files
    black  -> Passed
    ruff   -> Passed
    pytest -> Passed
```

`git diff --check` reported no whitespace errors.

Git emitted Windows working-tree CRLF/LF normalization warnings for several modified files; these are line-ending normalization notices and not validation failures.

---

## 11. M6 Production Changes

M6 includes focused production hardening in:

```text
app/api/dependencies.py
app/config/ai_settings.py
```

The changes provide:

* explicit supported-provider validation;
* fail-closed handling of unsupported providers;
* early OpenAI credential validation;
* per-instance environment evaluation for AI settings.

No provider execution authority was transferred to the V10 intelligence architecture.

---

## 12. M6 Test Changes

M6 introduces:

```text
app/tests/integration/test_v11_m6_2_provider_integration.py
app/tests/integration/test_v11_m6_3_provider_error_contracts.py
app/tests/integration/test_v11_m6_4_canonical_live_provider.py
app/tests/integration/test_v11_m6_5_provider_failure_contracts.py
```

Legacy live-test environment isolation was also corrected in:

```text
app/tests/integration/test_openai_live.py
app/tests/integration/test_summarize_live.py
```

---

## 13. Certification Decision

V11 M6 — Provider Integration & Controlled Real-Provider Validation is certified complete.

The system has demonstrated:

* canonical offline provider execution;
* explicit provider selection;
* fail-closed provider configuration;
* credential validation;
* controlled real-provider execution;
* safe provider failure handling;
* deterministic timeout handling;
* malformed-response containment;
* test-process environment isolation;
* architecture compatibility;
* complete non-live regression compatibility.

M6 introduces no unresolved architectural blocker for V11 M7.

**M6 certification result: PASS.**
