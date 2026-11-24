# TA.5 formal qualified closure and TA.7 transition — 23 November 2026 EST

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**Owner direction:** “Close TA5 and proceed to TA7. Give me a handoff prompt.”  
**Candidate:** `BCPL-0.1.0-rc4` / `BC0004` / `native_compiler: absent`  
**TA.5 — Native Runtime, Libraries, and Extensions Distribution:** FORMALLY CLOSED (qualified)  
**TA.6 — Native Cambridge Compiler Distribution and Self-Compilation:** N/A for RC4, not PASS or formal closure  
**TA.7 — Clean-Target Integration and Release Acceptance:** OPEN / IN PROGRESS

## Accepted TA.5 gate

The owner formally accepts the [revised distribution-only scope and evidence review](ta5-distribution-only-scope-and-acceptance-20261123.md), committed at `6f73dfd2f22f128dd387534581ad360b2a88e573`. RC4 manifest sequences 13–20 contain eight native PDSes and 41 members; the previously accepted actual MVS TA.3 NATIVE and COMBINED recipient results establish distribution inventory and installation. Native sources and supporting artifacts, including existing objects, are distributed as work in progress. No new native build, object reproducibility comparison, application generation, linkage, execution or regression was performed or is required for this candidate. Functional testing is restricted to the MR10 Kit Compiler until a full native Cambridge Compiler is available. Historical development evidence is not a new release acceptance claim.

The accepted NATIVE and COMBINED profiles at HERC02.BCPL.R4NT and HERC02.BCPL.R4CB contain 11 PDSes/71 members and 20 PDSes/150 members respectively. The MR10 profile at HERC02.BCPL.R4MR contains 11 PDSes/94 members. Preserve these installations and private accepted TA.3 and TA.4 receipts, which remain owner-reported evidence; this review did not directly inspect raw private reports.

The immutable candidate `mvs-state/tape/bcpl-0.1.0-rc4-BC0004.aws` retains recorded SHA-256 `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`. Preserve BC0003 and all no-retry markers. No replay of accepted production, installation or TA.4 verification on the existing system is authorized. Do not reopen TA.0–TA.5 without a demonstrated defect.

## TA.7 opening

Proceed with the [TA.7 kickoff](ta7-kickoff-20261123.md). Independently verify all three installation profiles on a clean MVS 3.8J target, using the unchanged tape and MVS-only recipient installation procedures. Functional release acceptance is MR10-only: the complete twelve-case semantic panel with fixed EXP, actual RP, TEST and CODE records compared against independent goldens, plus eleven language and seventeen BCPL demonstrations. Verify the included native and Cambridge source inventory and installation only. Do not substitute interpreter-hosted CAMBCOMP for a native compiler.

First establish clean-target isolation and discuss the major execution design with the owner. No new target IPL, stateful MVS operation, tape rewrite, or publication is authorized by this closure. TA.8 provenance/rights audit and controlled publication remain separately gated.
