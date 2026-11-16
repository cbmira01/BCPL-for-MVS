# CO.5 — Reproducible coroutine clean-room integration

**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Owner direction:** Extend the manifest and both reconstruction
entry points; install the modules, check inventory and rerun the oracle.
**Status:** Git implementation prepared; **fresh MVS reconstruction
not yet executed**. CO.5 IN PROGRESS.

## Single source of authority

`config/dspal.yaml` now maps Git-backed native coroutine sources,
header and JCL:
- `BOOT_SOURCE(COROUTIN)` and `BOOT_SOURCE(COHDR)` from the
  production BCPL library and public declarations;
- `BOOT_ASM(BCPLCO)` from the owner-promoted System/370 assembler;
- `BOOT_JCL(BLDCORCO)` and `BOOT_JCL(BLDCORLB)` from approved
  IFOX object installers with persistent-readback IEBCOMPR.

`BOOT_ASM(COROUTIN)` is **not** a Git-backed IFOX source or an
initial `generated_members` entry. After Guide Step 6 builds
resident CAMBCOMP, `compile-mvs` compiles
`bootstrap-toolchain/library/coroutines.bcpl` under the accepted
`/CN` Cambridge parameters. The accepted alias/export preparer
writes the independently assembled `CO3LIB` IFOX cards, then
`dspal put` stages the result as `BOOT_ASM(COROUTIN)`.

## Two reconstruction entry points

The simple `tools/reconstruction/rebuild-from-source` and guarded
`tools/reconstruction/run --run` both implement the identical
order: rebuild interpreter → resident CAMBCOMP → compile/prepare/
stage COROUTIN → build seven native runtime objects → build BLIB →
install `BCPLCO` → install `COROUTIN` → check exact **10-member**
`BOOT_OBJ` → independently compile/link/run accepted CO.3
delete/reuse application against installed objects → install System
Extensions. No candidate object is substituted into BOOT_OBJ.
Both builders retain previous explicit authorization/operating gates.

The guarded controller extends its immutable authorization and
provenance ledger, validates the compiler and staging receipts,
verifies complete four-step IFOX/IEBGENER/readback/IEBCOMPR
payloads with severity zero, inspects the exact object inventory
and cross-checks the independent GO result JSON against the
authorized Git revision, job IDs, and 21 accepted output records.

## Acceptance still outstanding

Run synthetic host tests first. An MVS clean-room rebuild **purges
all managed BCPL datasets and removes disposable workarea output**;
the owner must inspect the scope and ensure other JES submitters are
quiescent before invoking the unattended or guarded option. Then
retain new JOB identities, JES detail, assembler severities, object
readback receipts, installed-only IEWL map and oracle evidence.
If the production rebuild succeeds, rerun the applicable full suites
and request separate owner acceptance of CO.5 before declaring it
closed. The qualified CO.4 limits and known MR10 fixed-stack FAIL
remain unchanged.

## 16 November 2026 — completed clean-room reconstruction

The owner ran the new Git-integrated simple rebuild with bounded
batch population and reported **RC=0**, strict **10-member BOOT_OBJ
PASS**, installed coroutine **PASS**, compiler JOB **6489**, native
JOB **6490**, IFOX/IEWL/GO RC=0000 and 2m47s elapsed. The original
"not yet executed" status above describes this document at creation;
the current clean-room gate is now satisfied as recorded in
[CO.5 production clean-room PASS](co5-production-clean-room-pass-20261116.md).
Post-reconstruction full regression and formal CO.5 owner closure
remain outstanding.
