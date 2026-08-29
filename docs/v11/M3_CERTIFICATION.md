# V11 M3 Architecture Certification

## Scope

M3 integrates the validated V10 bounded-intelligence lifecycle into the
canonical V11 application path. It does not add a second execution path or
change ownership of the V7/V8 runtime, V9 summarization pipeline, or V10
intelligence contracts.

## Certified invariants

- `PRESERVE` and `ADVISORY` retain existing execution behavior and cannot
  authorize execution changes.
- `REVIEW` fails before pipeline or provider execution.
- `CONSTRAINED` is accepted only with execution authority and bounded-
  constraint proof.
- Invalid directives and insufficient authority fail closed before handoff.
- Observation and feedback are created from completed execution facts and are
  descriptive only; feedback does not re-enter intelligence control flow.
- Explainability and observability values cross only through immutable,
  read-only application metadata.
- The API application layer has no direct V10 implementation dependency.
- V10 integration has no provider, runtime, V9 pipeline, or execution-engine
  dependency.
- Existing V9 pipeline behavior remains the default execution behavior.

## Closure

M3 is certified when the focused M3/application/core/architecture suite and
the single full non-live regression are green. This document records the
certification result for the M3.6 review and does not create a release tag.
