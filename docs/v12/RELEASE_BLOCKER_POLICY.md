# AI Summarizer — V12 Release-Blocker Classification Policy

## 1. Purpose

This document defines the defect severity, release-blocker classification, triage, remediation, and closure policy for AI Summarizer V12.

It operationalizes the governance rules established by `V12_GOVERNANCE.md`.

The policy applies to findings discovered during:

- production stabilization
- regression testing
- integration certification
- security certification
- operational certification
- deployment validation
- packaging validation
- clean-install testing
- documentation certification
- release-candidate certification
- final release verification

The purpose is to ensure that release decisions are based on reproducible evidence and production impact rather than convenience, schedule pressure, or arbitrary test outcomes.

---

## 2. Classification Principles

Every V12 finding must be evaluated according to its actual effect on the supported production product.

Classification must consider:

1. **Impact** — what happens when the defect occurs?
2. **Reachability** — can it occur through a supported production path?
3. **Likelihood** — how realistically can it occur?
4. **Recoverability** — can an operator or user safely recover?
5. **Workaround** — is a practical documented workaround available?
6. **Security exposure** — does it create confidentiality, integrity, or availability risk?
7. **Operational impact** — does it prevent reliable deployment, diagnosis, or recovery?
8. **Release integrity** — does it invalidate the distributed artifact or certified source identity?

Severity must not be inflated merely because a test fails.

Likewise, severity must not be reduced merely because a defect is difficult to fix.

---

## 3. Severity Levels

V12 uses four primary defect severity levels:

```text
P0 — Critical
P1 — Production Blocking
P2 — Significant Non-Blocking
P3 — Minor
```

P0 and P1 are mandatory release blockers.

P2 and P3 require documented disposition but do not automatically block release.

---

## 4. P0 — Critical

### Definition

A P0 defect represents catastrophic production risk or makes a valid release fundamentally impossible.

Typical characteristics include one or more of:

- severe security compromise
- catastrophic data or state corruption
- application fundamentally unusable
- release artifact fundamentally invalid
- widespread failure with no safe workaround
- release identity cannot be trusted
- critical behavior creates unacceptable production risk

### Examples

Potential P0 examples include:

- secrets are exposed to unauthenticated users
- release package contains credentials or other critical sensitive material
- the packaged application cannot start in any supported deployment
- the final artifact does not correspond to the certified/tagged source
- a supported primary operation causes catastrophic corruption
- the release mechanism consistently produces unusable artifacts

### Release decision

```text
P0 FOUND     → RELEASE BLOCKED
P0 OPEN      → RELEASE BLOCKED
P0 RESOLVED  → FULL AFFECTED RECERTIFICATION REQUIRED
```

No P0 defect may be waived for final release.

---

## 5. P1 — Production Blocking

### Definition

A P1 defect materially prevents safe, correct, reliable, supportable, or documented use of a supported production capability.

The product may technically run, but the defect invalidates production readiness.

### Typical P1 conditions

Examples include:

- canonical supported application flow fails
- valid summarization requests fail systematically
- serious incorrect behavior occurs on supported input
- clean installation cannot be completed using release documentation
- mandatory production configuration cannot be established
- application startup is unreliable under supported configuration
- application cannot safely handle expected provider failures
- critical operational failures cannot be diagnosed
- a serious security vulnerability affects a supported production path
- required secrets are handled unsafely
- release packaging omits mandatory runtime components
- mandatory release documentation gives instructions that prevent correct deployment
- a required release certification gate fails

### Release decision

```text
P1 FOUND     → RELEASE BLOCKED
P1 OPEN      → RELEASE BLOCKED
P1 RESOLVED  → AFFECTED RECERTIFICATION REQUIRED
```

No unresolved P1 defect may remain in `v12.0.0`.

---

## 6. P2 — Significant Non-Blocking

### Definition

A P2 defect materially affects quality, reliability, usability, operations, or maintainability but does not invalidate the supported production release.

A practical workaround or acceptable operational mitigation normally exists.

### Examples

Potential P2 examples include:

- uncommon supported edge case fails but has a safe workaround
- noncritical diagnostic information is incomplete
- minor operational workflow requires an additional documented step
- a secondary error message is unclear but does not expose sensitive information
- packaging behavior is inconvenient but remains reproducible and correct
- documentation omits nonessential detail
- performance degradation exists but remains within acceptable production boundaries

### Required disposition

Every P2 must receive one of:

```text
FIX BEFORE RELEASE
DOCUMENT AS KNOWN LIMITATION
DEFER WITH ACCEPTED RISK
RECLASSIFY WITH EVIDENCE
```

The disposition must include rationale.

A P2 must be promoted to P1 if further evidence shows that it materially blocks safe or supported production operation.

---

## 7. P3 — Minor

### Definition

A P3 finding has low production impact and does not materially affect correctness, security, reliability, deployment, or supportability.

### Examples

Potential P3 examples include:

- cosmetic presentation issue
- minor wording inconsistency
- nonessential documentation improvement
- low-impact developer-experience issue
- harmless log formatting inconsistency
- minor usability inconvenience

### Release decision

P3 findings do not normally block release.

They may be:

- fixed when the change is extremely low risk and within V12 scope
- documented
- deferred to post-V12 work

P3 findings must not be used as justification for uncontrolled cleanup during release-candidate stabilization.

---

## 8. Release-Blocking Matrix

| Area | Example condition | Default classification | Release effect |
|---|---|---:|---|
| Security | Critical credential/secret exposure | P0 | Block |
| Security | Serious exploitable production weakness | P1 | Block |
| Application | Canonical application path unusable | P1 | Block |
| Summarization | Primary supported summarization path fails | P1 | Block |
| Installation | Clean supported installation impossible | P1 | Block |
| Startup | Supported production startup impossible | P1 | Block |
| Configuration | Mandatory configuration cannot be safely established | P1 | Block |
| Operations | Critical failure cannot be safely diagnosed/recovered | P1 | Block |
| Packaging | Release artifact unusable | P0/P1 | Block |
| Release integrity | Artifact does not match certified source | P0 | Block |
| Documentation | Mandatory deployment instructions are materially incorrect | P1 | Block |
| Documentation | Nonessential detail missing | P2/P3 | Assess |
| Performance | Production requirement demonstrably violated | P1/P2 | Assess |
| Cosmetic | Presentation-only defect | P3 | Do not block |

The matrix supplies default guidance only.

Final classification must use actual evidence and production impact.

---

## 9. Automatic Release-Blocker Conditions

Regardless of initial defect label, the release is blocked if any mandatory V12 certification condition remains unsatisfied.

Automatic blocker conditions include:

```text
Unresolved P0 defect
Unresolved P1 defect
Mandatory regression suite failure
Mandatory security certification failure
Mandatory operational certification failure
Mandatory clean-install certification failure
Mandatory packaging certification failure
Release artifact cannot be reproduced
Release artifact/source identity mismatch
Required production documentation absent or materially incorrect
Final repository/tag/version integrity failure
```

---

## 10. Test Failure Classification

A failed test is evidence of a finding; it is not itself a severity classification.

When a test fails:

```text
Test failure
    ↓
Determine failed contract
    ↓
Determine whether contract is supported/mandatory
    ↓
Assess production impact
    ↓
Assign P0/P1/P2/P3
    ↓
Determine release disposition
```

Examples:

- A canonical application regression test exposing a broken supported path may be P1.
- A test detecting catastrophic release-integrity failure may be P0.
- A minor documentation-format validation failure may be P3.
- A failure in an explicitly unsupported or obsolete scenario may require test correction rather than product remediation.

Tests must not be deleted, skipped, or weakened solely to avoid release-blocker classification.

---

## 11. Security Finding Classification

Security findings must be assessed according to exploitability and production impact.

Consider:

- attacker prerequisites
- affected interface
- confidentiality impact
- integrity impact
- availability impact
- secret exposure
- supported deployment assumptions
- practical mitigation
- residual risk

Security findings with uncertain severity should initially receive the higher reasonable classification until evidence supports reduction.

A security finding must never be downgraded solely to permit release.

---

## 12. Performance Finding Classification

Performance findings are release blockers only when supported by an explicit or defensible production requirement.

Performance classification must consider:

- supported workload
- input size
- concurrency
- provider behavior
- resource consumption
- timeout boundaries
- application responsiveness
- operational stability

A theoretical optimization opportunity is not a V12 defect.

Performance work without demonstrated production impact is outside V12 scope.

---

## 13. Documentation Finding Classification

Documentation defects can be production blockers.

A documentation finding is normally P1 when following the official release instructions prevents a competent user or operator from successfully:

- installing the application
- configuring mandatory settings
- starting the application
- accessing the supported product
- safely operating it
- identifying mandatory security requirements

Minor omissions or clarity improvements normally classify as P2 or P3.

---

## 14. Packaging Finding Classification

Packaging is part of the V12 product.

A packaging defect may be P0 or P1 when:

- the release artifact cannot be installed
- mandatory runtime files are missing
- dependencies cannot be resolved under the supported environment
- artifact contents differ materially from certified source
- version identity is incorrect
- the artifact cannot be reproduced
- documented startup cannot work from the distributed release

Packaging inconvenience without functional or operational impact may be P2/P3.

---

## 15. Finding Record

Every release-relevant finding should contain sufficient information for independent review.

Recommended record:

```text
Finding ID:
Title:
Date:
Detected during:
Affected version/commit:
Area:
Severity:
Release blocker: YES/NO

Description:
Reproduction:
Expected behavior:
Actual behavior:
Production impact:
Workaround:
Evidence:

Disposition:
Resolution:
Regression tests:
Residual risk:
Status:
```

Not every minor P3 observation requires extensive documentation, but all P0/P1 and release-relevant P2 findings must be traceable.

---

## 16. Status Model

Release-relevant findings use the following lifecycle:

```text
OPEN
  ↓
TRIAGED
  ↓
CONFIRMED
  ↓
IN REMEDIATION
  ↓
FIXED
  ↓
VERIFIED
  ↓
CLOSED
```

Alternative terminal states for non-blocking findings may include:

```text
DEFERRED
KNOWN LIMITATION
NOT A DEFECT
DUPLICATE
```

P0/P1 findings cannot reach `DEFERRED` for the final `v12.0.0` release.

---

## 17. Severity Reclassification

Severity may change when new evidence becomes available.

Any reclassification must document:

```text
Previous severity:
New severity:
Evidence:
Reason:
Release impact:
```

Examples:

- P2 → P1 because the issue affects the canonical production path.
- P1 → P2 because testing demonstrates the affected scenario is outside the supported deployment contract and a safe supported path remains available.

Reclassification must be evidence-based.

---

## 18. Remediation Rules

A V12 defect correction must:

1. address the demonstrated defect
2. remain as narrow as practical
3. avoid unrelated refactoring
4. preserve frozen V11 architecture whenever possible
5. include appropriate regression coverage
6. pass applicable V12 certification gates

A defect must not be used as an opportunity to introduce unrelated improvements.

---

## 19. Architecture-Affecting Defects

If remediation appears to require changing a frozen V11 architectural boundary, the V12 production-blocking architecture exception process defined in `V12_GOVERNANCE.md` applies.

Architecture-affecting remediation requires explicit evidence that:

- the defect is production-blocking
- the existing boundary cannot reasonably be preserved
- the proposed correction is minimal
- regression certification protects established V11 contracts

P2 or P3 findings do not justify architecture redesign.

---

## 20. Closure Requirements

A P0/P1 finding is not closed merely because code has been changed.

Closure requires:

```text
Defect reproduced
Root cause understood
Correction implemented
Targeted regression test passes
Affected certification area passes
Required broader regression passes
No new release blocker introduced
Finding evidence updated
```

Where relevant, clean-install, packaging, security, or operational certification must also be repeated.

---

## 21. Release-Candidate Rules

During RC stabilization, a newly discovered finding is handled as follows:

```text
P0 → stop release, remediate, recertify, issue new RC
P1 → stop release, remediate, recertify, issue new RC
P2 → assess risk; fix only when justified and low risk
P3 → normally defer
```

Every change to an RC invalidates the affected portion of its previous certification evidence.

A replacement RC must be generated when release artifact source changes after RC certification.

---

## 22. Final Release Gate

The final `v12.0.0` release requires:

```text
P0 open: 0
P1 open: 0
Mandatory certification failures: 0
Unresolved artifact-integrity failures: 0
Unresolved clean-install blockers: 0
Unresolved mandatory documentation blockers: 0
```

P2/P3 findings, if any, must have documented disposition.

---

## 23. Governing Decision

V12 release decisions are based on demonstrated production impact and certification evidence.

The project will not:

- hide failing evidence
- weaken certification to achieve release
- waive P0/P1 findings for schedule reasons
- expand architecture to address non-blocking improvements
- treat every imperfection as a release blocker

The objective is a controlled, evidence-backed production release of the frozen V11 product architecture.