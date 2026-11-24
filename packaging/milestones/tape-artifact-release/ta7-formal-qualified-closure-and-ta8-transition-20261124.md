# TA.7 formal qualified closure and TA.8 transition — 24 November 2026 EST

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**Owner direction:** “Close TA7 and give me a handoff prompt to implement TA8.”  
**Candidate:** BCPL-0.1.0-rc4 / BC0004 / native_compiler: absent  
**TA.7 — Clean-Target Integration and Release Acceptance:** FORMALLY CLOSED (qualified)  
**TA.8 — Release Audit and Controlled Publication:** OPEN / IN PROGRESS

The owner formally closes TA.7 on the basis of the [superseding clean-namespace decision](ta7-clean-namespace-decision-20261124.md) and the [technical acceptance record](ta7-clean-namespace-acceptance-20261124.md) committed at 82beeb1a64dbe7f0954e89157561605c85c21c7e.

Accepted owner-reported actual MVS evidence: JOB 9423 established 42 absent target PDSes; HERC02.BCPL.T7MR, T7NT and T7CB restored 11/94, 11/71 and 20/150 PDSes/members respectively. MR10 JOBS 9431/9433/9435 and COMBINED JOBS 9447/9449/9451 passed 56 demonstrations and 24 automatic TEST/EXP/RP/CODE regression verdicts, 80/80 functional cases, with 326 required functional steps. The original evidence remains at workarea/ta7-clean-namespace/20261124T133036Z-41593. The assistant did not independently open the private raw reports or seal. This is clean-namespace qualification on the existing MVS system, not independent-system IPL or alternate HLQ certification. Native components and Cambridge sources are distribution-only work in progress; TA.6 remains N/A for RC4.

Preserve exact RC4 AWS bytes at mvs-state/tape/bcpl-0.1.0-rc4-BC0004.aws, SHA-256 7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1, the original BC0003, prior accepted namespaces and all private evidence and consumed no-retry markers. Do not rerun accepted work absent a demonstrated defect.

Open TA.8 under the existing formal milestone gate. Proceed with [TA.8 kickoff](ta8-kickoff-20261124.md). Audit provenance and redistribution, scope disclosure, version/VOLSER registry, documentation, checksum, manifest and evidence. Only exactly tested bytes may be published, subject to a separate explicit publication decision. A verified release without the native compiler is eligible, but do not claim a complete native compiler or a complete two-compiler release. No stateful MVS operation, tape modification, new candidate identity, public tag/release/asset or publication is authorized by this closure.
