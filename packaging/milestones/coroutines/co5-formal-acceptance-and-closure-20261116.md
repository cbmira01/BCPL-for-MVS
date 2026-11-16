# CO.5 — Integration, Regression, and Release: formal qualified closure

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Owner decision:** **ACCEPTED AND CLOSED (qualified)**
**Decision date:** 16 November 2026
**Source review checkpoint:** GitHub `main` `52df97e0b06a9808e36537c5836caf67001214d1`
**Post-clean-room tested source:** `9a621d5aac0d5c6068e10c6425b861f7480cf30a`
**Next proposed work:** CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification (**PROPOSED; not established**)

## Explicit owner decision

The owner wrote: **“I approve, close CO.5 right now, give me a
handoff prompt to CO.6.”** This is explicit acceptance of the
[formal qualified acceptance review candidate](co5-qualified-acceptance-review-candidate-20261116.md).
CO.5 therefore transitions from IN PROGRESS to **CLOSED (qualified)**.

The accepted scope is specifically the bounded native System/370
coroutine integration and verification performed by the Cambridge
Compiler and the reconstructed runtime. This is a completed
qualified march, not an unlimited coroutine facility or a published
distribution release.

## Accepted source and target-system evidence

| CO.5 gate | Evidence and accepted result |
| --- | --- |
| Stable test ownership | Native coroutine tests 177–189 added without renumbering 00–176 |
| Production modules | `BOOT_OBJ(BCPLCO)` and `BOOT_OBJ(COROUTIN)`; owner-approved permanent G!289–300 assignments; installed object provenance and binary readback |
| Reproducible clean-room | MVS driver RC=0 in 2m47s, `BOOT_OBJ` 10 exact production members, regenerated and installed coroutine modules from Git-backed BCPL, IFOX and JCL |
| Independent installed-only GO | Cambridge JOB 6489, native JOB 6490, IFOX/IEWL/GO all RC0000 and accepted 21-record `CO3BCPL` oracle |
| Applicable post-rebuild regressions | Six selected regular production suites PASS, coordinator RC=0; 201 PASS, zero FAIL, expected SKIP 083, zero BLOCKED; includes BCPLQSAM device-authorized cases 175–176 and coroutine cases 177–189 |
| Source/recovery documentation | Git authority, reconstruction orchestration, exact object inventory, installation and recovery limits documented |

The clean-room receipt is preserved at
`mvs-state/reconstruction-evidence/co5-rebuild-20261116T005114Z.log`.
The complete post-rebuild regular regression receipt is preserved at
`mvs-state/reconstruction-evidence/co5-full-regressions-20261116T015902Z.log`
and `workarea/project-regressions/20261116T015903Z-89277-ukfu4oxd/summary.json`.
The owner provided MVS runner excerpts; complete raw individual JES
reports were not independently inspected in this chat.

Detailed evidence:
- [Git-driven clean-room reconstruction PASS](co5-production-clean-room-pass-20261116.md)
- [Full post-reconstruction production regular-suite PASS](co5-post-reconstruction-full-regression-pass-20261116.md)
- [Production approval and source provenance](co5-production-promotion-20261115.md)

## Explicitly retained negative evidence

The original interpreted MR10 Development Probe
`10-coroutines/fixed-stack-producer-consumer` remains **FAIL**
with interpreted CODE=-1 under the reconstructed canonical
startup-frame contract. Its separately verified compatible
COBOOT-framed variant PASS does not reclassify the original
accepted source, expected output or oracle. The eleven
development probes were previously **10 PASS, 1 FAIL**;
they were **not** part of the six-suite post-clean-room regular
PASS and are not represented as an all-PASS campaign.

The original Bootstrap case
`117-independent-input-eof` failed after native IFOX ASMAP
RC0000 because IEWL `LKED` in JOB 6745 abended **SB2D**;
GO never executed. A separately executed one-case retry PASS
and a later full-production-suite PASS demonstrated restored
normal behavior without source/oracle changes, but do not prove
the environmental/overlay root cause or erase the original FAIL.

See [MR10 negative evidence](co5-mr10-fixed-stack-negative-code-20261115.md)
and [Bootstrap 117 original SB2D and reruns](co5-bootstrap-117-post-cleanroom-abend-20261116.md).

## Qualified architecture and release boundary

The owner-accepted bounded **Approach A/S1** support covers a
root coroutine and **at most two live registered worker
coroutines**, independently checked fixed **1024-word** worker
stacks, transfers/wait/resume, normal termination, and
root-controlled deletion of known-live inactive descriptors
with registry revocation before reclamation. Global slots
**G!289–300** are permanently assigned for this native support.
The private 24-word descriptor is not a public representation
contract.

**Not accepted:** arbitrary/freed/stale descriptor-pointer safety,
ABA-proof handles, generalized size/worker counts, actual system
GETMAIN exhaustion recovery, deliberate stack overflow recovery,
exceptional cancellation and abend recovery, reentrancy,
multitasking/preemption, full historical interpreted-frame
compatibility, or guarantees for the future natively executing
Cambridge compiler.

Git-source reconstruction of the **current** accepted
installation has passed. Automatic rollback to a previous
object-library image, distribution tape creation, a release
artifact, and public release publication have **not** been
tested/authorized. No additional MVS build or object overwrite
was required to record this closure.

## Formal disposition

- CO.0 — Historical Research and Behavioral Contract: CLOSED (qualified)
- CO.1 — Native ABI and Stack Architecture: CLOSED (qualified)
- CO.2 — Native CHANGECO Implementation: CLOSED (qualified)
- CO.3 — Coroutine Library and Lifecycle: CLOSED (qualified)
- CO.4 — Robustness and Edge-Case Verification: CLOSED (qualified)
- **CO.5 — Integration, Regression, and Release: CLOSED (qualified, owner accepted 16 November 2026)**

**CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler
Verification** is the proposed next research/verification march
named in the handoff request; it is **not** an established entry
in the existing authoritative milestone and requires separate
scope/acceptance-gate approval. CO.5 closure must not be
reopened without a demonstrable regression or defect in its
accepted bounded implementation.

This is a **documentation-only closure**. No branch, MVS
job, resident dataset change, or public release was created.
