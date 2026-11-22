# TA.2 — Owner authorization: one BC0002 MVS readback

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST / 22 November 2026 UTC  
**Decision:** **APPROVED, NOT YET EXECUTED.**

The owner explicitly stated **“I approve readback operation”** following the separately proposed, exactly scoped one-shot BC0002 readback. The immutable machine-readable execution contract is `ta2-rc2-readback-execution-approval.json`; the existing `scripts/ta2-rc2-readback-once` validates its exact contents against Git `main` before doing any new MVS inquiry.

**Scope:** Mount the *existing* `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws` (SHA-256 `123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375`) on Hercules **0480** only if the drive is freshly verified **EMPTY** with MVS **O-NRD**; if the exact image is already mounted and verified, do not replace it. Submit **one** `TA2RC2RB` MVS job, **R0001** IEBGENER plus **R0002–R0021** IEBCOPY, to restore the **21** standard-label tape datasets as **new** `HERC02.BCPL.TA2RB.BT0001`–`BT0021` on **TSO002**. All output DDs require `DISP=(NEW,CATLG,DELETE)`; preserve `BT0012` as `PO/U/0/6144`. No source-stage or existing dataset may be overwritten.

**Pinned acceptance:** Original producer JOB **9339** and AWS structural PASS; read-only catalog JOB **9340** and VTOC JOB **9341**, which established **21 absent targets** and **15,335** reported free tracks. Accepted SHA256SUMS evidence: `workarea/ta2-rc2-readback-preflight/20261122T010923Z-28068`. The frozen JOB-less readback JCL SHA-256 is `226819ef3702234a1367c7a7df96399cf9fcaf32d99152061db1df98fed12e73`; do not regenerate or change the deck independently of its canonical manifest-driven planner.

**Safety:** Require a clean `main`, the exact committed approval, saved-evidence replay, an unchanged AWS hash, fresh source DCB and target-absence inquiries, the exact Hercules/MVS device state, and **one operator [y/N]** before mounting/submission. The runner creates a no-retry invocation marker before its fresh MVS inquiry and an irreversible intent marker before any mount/JES readback. On any failure or ambiguity **DO NOT RERUN**; preserve image, device state, original receipts, restored data and failure reports. No HETINIT, tape rewriting, automatic unmount, restaging, publication, or clean recipient installation is authorized.

**Verification:** The unchanged canonical planner and one-shot runner previously passed **37/37** local offline tests. Immediately before committing the authorization, the 20 approval schema keys and the runner's Git guard, permanent marker ordering and single-submission/no-unmount paths were independently rechecked against authoritative GitHub `main`. Actual MVS readback results remain the acceptance authority.

Successful job RC=0000 would establish qualified MVS readback, not member-byte equality or TA.2 closure; restored DCB/directory/content verification remains outstanding. **TA.2 IN PROGRESS.**
