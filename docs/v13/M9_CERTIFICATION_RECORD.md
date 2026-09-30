# V13 M9 Certification Record

Status: IN PROGRESS

Application identity during M9.2-M9.8: `13.0.0-rc1`

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

Status: CERTIFIED. The RC artifact was extracted into a clean location and installed into a fresh Python 3.11.9 virtual environment. `pip check` reported no broken requirements. Application identity was `13.0.0-rc1`. Direct `app` import and FastAPI application import passed. Packaged startup passed. `/`, `/docs`, and `/api/v1/product-config` returned successfully. Browser certification, TXT ingestion, and PDF ingestion passed. An initial runtime-validator failure was transient/nonreproducible; the exact command subsequently passed along with direct imports, packaged startup and HTTP validation, so no release defect was classified.

## M9.6 — Controlled Real-Provider Certification

Status: CERTIFIED. Exactly one controlled canonical live-provider test was executed through `/api/v1/summarize` using the existing OpenAI-compatible provider boundary. Result: `1 passed`. The test verified a nonblank summary, configured model identity, token accounting, strategy metadata, and `intelligence_mode == preserve`. Live credentials were then removed from the process environment. Post-live full offline regression: `5372 passed, 10 deselected`. `git diff --check` passed and tracked source remained clean.

## M9.7 — Release Documentation & Operational Readiness

Status: COMPLETE. Active product documentation has been migrated to V13 while historical V10-V12 documentation remains unchanged. The current documentation set includes README, CHANGELOG V13 section, repository guidance, V13 installation/configuration/operations/troubleshooting/release notes, and this certification record. Release-builder help text uses the V13 RC identity. Release tests passed: 30. Full non-live regression passed: 5372, with 10 live tests deselected. Pre-commit and git diff checks passed.

Because documentation is part of the release artifact, M9.7 invalidates the previous RC ZIP/checksum as final RC evidence. M9.8 must rebuild the RC artifact, establish a new deterministic checksum, rerun relevant packaging/clean-artifact smoke validation, and certify the exact candidate.

## Remaining

M9.8 — Release Candidate Certification: PENDING.

M9.9 — Final v13.0.0 Release & Remote Verification: PENDING.

Final identity requirement: local HEAD = local `v13.0.0^{}` = remote `main` = remote `v13.0.0^{}`, with all mandatory release gates passing, P0/P1 findings zero, and architecture exceptions zero.
