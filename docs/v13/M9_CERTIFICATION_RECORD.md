# V13 M9 Certification Record

Status: IN PROGRESS

Application identity during M9.2-M9.8: `13.0.0-rc1`.
Application identity during M9.9 final certification: `13.0.0`.

## M9.1 — Release Baseline & Certification Matrix

Status: COMPLETE. Starting certified V13 baseline: M8 commit `424deed36dbeba9e6acb619653e75c9d25cc3dd6`, tag `v13.0.0-m8`.

## M9.2 — Release Identity & Version Certification

Status: COMPLETE. Application identity established as `13.0.0-rc1`; V13 release-identity tests added; final/milestone identity excluded from the RC phase.

## M9.3 — Final Functional / Regression Certification

Status: COMPLETE. Combined M7/M8/identity suite: 1515 passed. API: 61 passed. Core: 142 passed. Integration: 1114 passed with 10 skipped. Frontend: 1014 passed. Release: 29 passed. Full non-live at this stage: 5371 passed, 10 deselected. Pre-commit and `git diff --check` passed.

## M9.4 — Packaging & Release Artifact Certification

Status: CERTIFIED. `PKG-V13-001` identified and closed: the active artifact initially included historical V12 documentation and omitted V13 documentation. The release allowlist was corrected to `docs/v13/` only and active artifact tests were migrated to V13. Corrected packaging tests: 18 passed. Complete release regression: 30 passed. Two independent RC1 builds produced the same SHA-256: `C6E8EABB0608D412DAC388CF6F917F41806592A70A02D343FB1D103271B6C95D`. This hash is superseded by M9.7 documentation changes and must not be used as the M9.8 RC hash.

Release-candidate identity/packaging checkpoint commit: `0ef2b7f95a6e4f65e9a7376cc18fc7fff894f602`.

## M9.5 — Clean-Install / Runtime / Browser Certification

Status: CERTIFIED. The RC artifact was extracted into a clean location and installed into a fresh Python 3.11.9 virtual environment. `pip check` reported no broken requirements. Application identity was `13.0.0-rc1`. Direct `app` import and FastAPI application import passed. Packaged startup passed. `/`, `/docs`, and `/api/v1/product-config` returned successfully. Browser certification, TXT ingestion, and PDF ingestion passed. An initial runtime-validator failure appeared nonreproducible during M9.5 and no defect was classified at that stage. M9.8 later reproduced the standalone-script failure conclusively in a fresh artifact, classified it as `RUNTIME-V13-001`, corrected it, added regression protection, and recertified the corrected packaged validator.

## M9.6 — Controlled Real-Provider Certification

Status: CERTIFIED. Exactly one controlled canonical live-provider test was executed through `/api/v1/summarize` using the existing OpenAI-compatible provider boundary. Result: `1 passed`. The test verified a nonblank summary, configured model identity, token accounting, strategy metadata, and `intelligence_mode == preserve`. Live credentials were then removed from the process environment. Post-live full offline regression: `5372 passed, 10 deselected`. `git diff --check` passed and tracked source remained clean.

## M9.7 — Release Documentation & Operational Readiness

Status: COMPLETE. Active product documentation has been migrated to V13 while historical V10-V12 documentation remains unchanged. The current documentation set includes README, CHANGELOG V13 section, repository guidance, V13 installation/configuration/operations/troubleshooting/release notes, and this certification record. Release-builder help text uses the V13 RC identity. Release tests passed: 30. Full non-live regression passed: 5372, with 10 live tests deselected. Pre-commit and git diff checks passed.

Because documentation is part of the release artifact, M9.7 invalidates the previous RC ZIP/checksum as final RC evidence. M9.8 must rebuild the RC artifact, establish a new deterministic checksum, rerun relevant packaging/clean-artifact smoke validation, and certify the exact candidate.

## M9.8 — Release Candidate Certification

Status: CERTIFIED. The post-M9.7 RC was rebuilt from the documented source state and subjected to deterministic packaging, artifact-boundary, clean-install, runtime, HTTP/API, file-ingestion, and browser certification.

During clean-artifact certification, `RUNTIME-V13-001` was conclusively reproduced: direct execution of `python scripts/validate_runtime.py` failed because the standalone script did not establish the project root on `sys.path`. The finding was classified P1 release-blocking. The validator was corrected to derive the project root from its own file location and regression coverage was added. Correction commit: `906dabdf44bb3994bfcd15f158b2d0debf4967d9`.

Post-correction validation passed: runtime-validator regression 1 passed; release suite 31 passed; full non-live regression 5373 passed with 10 live tests deselected; pre-commit passed; and `git diff --check` passed. Two independent corrected RC builds were byte-for-byte identical with SHA-256 `F2AB3A94284DB9B49F2B551DB32170B026FAA126CBB38CA1602CB3AE04485B98`.

The corrected artifact contained 495 normalized release entries, with zero entries outside the expected release root, zero historical V12 documentation entries, zero prohibited-content findings, and zero missing required files. The preserved artifact copy matched the build SHA-256 exactly.

The corrected artifact was then extracted into a fresh location and installed into a fresh production virtual environment. `pip check` reported no broken requirements. Packaged identity was `13.0.0-rc1`. Direct `app` import, FastAPI import, standalone runtime validation, and runtime validation from outside the release working directory with `PYTHONPATH` removed all passed. `/` and `/docs` returned HTTP 200. `/api/v1/product-config` exposed only product-safe model fields. Canonical fake-provider summarization returned a nonblank result. TXT extraction passed. PDF extraction passed with nonblank extracted text from a 32-page PDF. Browser certification passed.

`RUNTIME-V13-001` is CLOSED. Open P0/P1 release findings from M9.8: zero.

The SHA-256 above identifies the corrected M9.8 validation artifact. Because this certification record is itself packaged release content, this documentation-only M9.8 update necessarily changes the subsequent RC artifact hash. The final documented RC must therefore be rebuilt deterministically and its exact artifact identity and release boundary reverified before the RC tag is created. No application/runtime behavior is changed by this documentation update.

## M9.9 — Final v13.0.0 Release & Remote Verification

Status: PRE-PUBLICATION CERTIFIED. M9.9 began from the certified `v13.0.0-rc1` source/tag identity at commit `37859f241349a06edf0aa59f37e2f77873798114`. Final application identity `13.0.0` was established at source checkpoint commit `72ca5722c154911e7a6120dc96e1b561584d61e8`.

The M9.9 validation artifact was built twice from that checkpoint and was byte-for-byte deterministic. SHA-256: `828760DA37ED6B5A3ED742C6210758A1E6A66AB451702A85377EEADAD17CC975`. The archive contained 495 entries with zero paths outside the expected release root, zero historical V12 release documentation, zero prohibited content, and zero missing required release files. An exact validation copy was preserved outside the repository and its SHA-256 was independently reverified.

The validation artifact was extracted into a fresh location and installed into a fresh production virtual environment. `pip check` reported no broken requirements. Packaged application identity was `13.0.0`. Direct `app` import, FastAPI import, standalone runtime validation, and runtime validation from outside the release working directory with `PYTHONPATH` removed all passed.

Packaged Uvicorn startup passed. `/` and `/docs` returned HTTP 200. `/api/v1/product-config` exposed only the approved public product-model fields and exactly one default model. Canonical fake-provider summarization returned a nonblank result with the expected packaged runtime metadata.

TXT extraction passed through the public multipart extraction boundary. PDF extraction passed using the known-good `AIForAll-Week8.pdf` certification fixture with 32 pages and nonblank extracted text.

Packaged browser certification passed for application load/version, paste-and-summarize, result workspace and console sanity, Copy, UTF-8 TXT Download, Regenerate, Processing details, TXT browser upload, PDF browser upload, responsive behavior, focus visibility, and product sanity. The certification server was then cleanly stopped.

M9.9 release identity tests passed: 11 tests. Release regression passed: 31 tests. Full non-live regression passed: `5373 passed, 10 deselected`. Pre-commit passed and `git diff --check` passed. Open P0/P1 release findings: zero. New architecture exceptions: zero.

The SHA-256 above identifies the immutable M9.9 pre-publication validation artifact. Because this certification record and the associated release-status documentation are themselves packaged release content, this documentation-only checkpoint necessarily changes the subsequent final artifact hash. The exact final distributable must therefore be rebuilt deterministically from the documentation checkpoint, its release boundary and packaged runtime reverified, and its exact SHA-256 preserved before the final `v13.0.0` tag is created.

Final publication has not yet occurred. Publication requires the exact final artifact certification, annotated `v13.0.0` tag creation, push of `main` and the final tag, and verification that local HEAD, local final-tag dereference, remote `main`, and remote final-tag dereference all identify the same certified commit.

Final identity requirement: local HEAD = local `v13.0.0^{}` = remote `main` = remote `v13.0.0^{}`, with all mandatory release gates passing, P0/P1 findings zero, and architecture exceptions zero.
