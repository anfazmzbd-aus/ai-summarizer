# V12 PKG-002 Packaging Correction Record

## Finding

```text
Finding: PKG-002
Area: Standalone release packaging
Initial severity: P1 — Release Blocking
Status: FIXED AND RECERTIFIED
```

During V12 M5 documentation validation, inspection of the generated standalone artifact revealed that the release ZIP contained Git-tracked development, runtime, legacy, and historical material that was outside the intended V12 standalone release boundary.

Observed prohibited examples included:

```text
summaries.db
requirements-dev.txt
requirements_test.txt
requirements_now.txt
requirements_f.txt
pyproject.toml
Makefile
app/legacy/
app/tests/
docs/V9/
docs/v11/
docs/releases/
docs/DECISIONS/
```

This contradicted the standalone packaging policy established and certified during V12 M4.

---

## Root Cause

The release builder:

```text
scripts/build_release_artifact.py
```

obtained the Git-tracked file set and applied a small exclusion list.

The inclusion policy therefore behaved as:

```text
all Git-tracked files
minus explicitly excluded files
```

Any tracked file not explicitly excluded was silently admitted into the release artifact.

The dedicated packaging tests validated representative inclusion/exclusion cases but did not inspect the complete generated ZIP boundary.

---

## Correction

The release builder was changed to an allowlist-oriented release model.

Permitted release content is limited to:

```text
.env.example
CHANGELOG.md
README.md
requirements.txt

app/
  excluding app/tests/
  excluding app/legacy/

static/

docs/v12/

scripts/build_release_artifact.py
scripts/validate_runtime.py
```

Unrecognized tracked repository files are now excluded by default.

No application architecture, provider architecture, summarization behavior, intelligence behavior, public API contract, or runtime orchestration boundary was changed.

---

## Deterministic Construction

The ZIP writer was also hardened to use deterministic archive metadata rather than source-file modification timestamps.

Two independent builds from the same source and version produced the identical SHA-256 value:

```text
981BF1C49533A5AE4BE296B4BE6298C3D5129A43138B742488203EC8E9BDB8A2
```

Result:

```text
Deterministic construction: PASS
```

---

## Packaging Test Strengthening

The release packaging suite was expanded from representative policy tests to include:

* explicit legacy exclusion,
* runtime-database exclusion,
* development-requirements exclusion,
* development-tooling exclusion,
* historical-documentation exclusion,
* default-deny behavior,
* actual generated ZIP manifest validation,
* checksum validation,
* deterministic build validation.

Dedicated result:

```text
17 passed
```

---

## Artifact Boundary Validation

The corrected artifact was inspected after extraction.

Required release material was present.

Prohibited release material was absent.

Result:

```text
Release boundary: PASS
Artifact hygiene: PASS
```

---

## Clean-Install Recertification

The corrected minimal standalone artifact was extracted outside the development repository.

A fresh Python 3.11 virtual environment was created.

Only:

```text
requirements.txt
```

was used to install runtime dependencies.

The application was configured using:

```text
AI_PROVIDER=fake
OPENAI_MODEL=demo
```

and started using:

```text
uvicorn app.main:app --host 127.0.0.1 --port 8002
```

Validation covered:

```text
GET /
GET /docs
POST /api/v1/summarize
clean shutdown
```

Result:

```text
CERT-PKG   PASS
CERT-CLEAN PASS
```

---

## Regression Recertification

The full non-live regression suite and repository quality gates were rerun after the packaging correction.

Required final evidence:

```text
release packaging tests: PASS
full non-live regression: PASS
pre-commit: PASS
git diff --check: PASS
```

---

## Architecture Assessment

```text
Architecture exception required: NO
```

The correction is confined to V12 packaging and release-certification tooling.

The frozen V11 canonical application architecture remains unchanged.

---

## Final Disposition

```text
PKG-002
Status: FIXED
Release-blocking condition: CLEARED
CERT-PKG: PASS
CERT-CLEAN: PASS
```

The repository may proceed to V12 M6 Release Candidate Certification after the corrective commit is completed and synchronized.
