# TA.2 — Owner-approved 21-dataset MVS readback: JCL and read-only preflight implementation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST / 22 November 2026 UTC  
**State:** **DESIGN APPROVED; offline JCL rendering and MVS-facing read-only preflight implemented/tested. No readback execution or new DASD allocation authorized.**

## Owner decision and accepted AWS starting point

The owner explicitly approved the proposed independent readback design following the qualified original MVS `TA2RC2WR` **JOB 9339**, 21/21 RC=0000, 21 SL datasets, 64 physical files and 2,559 reconciled tape blocks. The accepted original AWS is `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`, 1,957,296 bytes, immutable SHA-256 `123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375`; accepted private review evidence remains `workarea/ta2-rc2-postwrite-audit/20261122T001850Z-27778`. The permanent write-attempt marker must not be modified.

Design approval allows implementation and host-only testing; it does **not** approve a particular new scratch DASD volume, allocation, tape positioning, new MVS dataset creation, or the 21-step tape readback job.

## Implemented and reviewed source

The new `packaging/distribution/create-tape/scripts/ta2-rc2-readback-plan` performs:

1. An unchanged replay of the official **`BCPL-0.1.0-rc2`** manifest and original frozen **write-JCL SHA-256** `85eca6f3e1e83c2d0e476f24870a20664bde2a50e2de8653606bfa351af54b4f` using the existing producer and accepted 21 input-stage receipts; no competing manifest or registry.
2. A deterministic **JOB-less** 21-step proposed readback deck: **R0001 IEBGENER** from tape `LABEL=(1,SL)`, then **R0002–R0021 IEBCOPY** from `LABEL=(2,SL)`–`(21,SL)`. The tape DDs are input-only `DISP=OLD` with `VOL=(PRIVATE,RETAIN,SER=BC0002)`. Each output is a **NEW**, separately cataloged `HERC02.BCPL.TA2RB.BTnnnn` scratch DASD dataset on an explicitly specified volume. Consecutive steps use `COND=(0,NE)` to avoid continuing after a failed step; no tape output, HETINIT, mount, unmount or retry commands exist.
3. Exact source-manifest DCB on restored targets: `BT0001 PS/FB/80/800`, all text PDSes `PO/FB/80/800`, and **`BT0012 PO/U/0/6144`**. The selected PDS total is **146** members, including the four generated installer members and fifteen Cambridge historical source members.
4. A proposed track budget derived from **the accepted staging *reference*, not approved for readback**: original `BT0003`–`BT0020` stage allocations total 645 primary + 65 secondary tracks; proposed `BT0001` 5+1, `BT0002` 20+5, and `BT0021` 100+10. **Overall proposed 770 primary + 81 secondary tracks**, plus 100 tracks of screening margin. Directory blocks use the original worksheet for positions 3–20; `BT0002` and `BT0021` propose 10.
5. An optional **read-only MVS-facing preflight** (`--volume <DASD_VOL> --live`) which checks the original AWS SHA and qualified sealed receipt, exact Docker tape bind and mounted Hercules device 0480, MVS drive readiness, 21 scratch target catalog absences and 21 accepted source DCBs via one LISTDS inquiry job, then a formatted IEHLIST VTOC inquiry for candidate allocation space and uncataloged target collisions. It preserves original reports and SHA256SUMS under a new `workarea/ta2-rc2-readback-preflight/` evidence folder, printing only job IDs, reported space and PASS/refusal. The IEHLIST free-space report is a **screening result, not a complete free-extents certification**.

The volume argument has **no default** and rejects reserved scratch/tape serials. A different chosen DASD VOLSER changes the generated JCL hash and must be reviewed and bound to a subsequent separate owner write/read approval.

## Verification and execution boundary

The exact new script and companion `tests/test_ta2_rc2_readback_plan.py` were tested in the assistant's separate repository-root workspace: **12/12 synthetic offline checks PASS**, Python AST PASS. They cover all 21 DDs and 21 source-to-target positions, the `BT0012` binary DCB, 146-member/770+81-track totals, 71-column JCL operands, refusal of bad volume/sequence/manifest DCB/space drift, and absence of all state-changing tape commands. The created Git blob identities were checked against locally tested `git hash-object` values.

**Not implemented or authorized in this checkpoint:** a stateful `--run` argument, tape positioning, JCL submission for the actual 21-step readback, scratch DASD allocation, restored member/record comparisons, IEHLIST/executable-use follow-up for `RECFM=U`, clean recipient installation or publication. Subsequent one-shot runner implementation must be owner-reviewed with exact volume, readback-JCL SHA and actual read-only MVS preflight evidence. No approval file for a stateful readback is created here.

**TA.2 remains IN PROGRESS.** Only the existing qualified AWS structure is accepted; full MVS readback/content verification still remains.

## Live design preflight refused: read-only device diagnosis pending

The owner reported `--volume TSO002 --live` **RC=2**: Hercules 0480 did not demonstrate the expected attached BC0002 image. The original sealed error evidence resides in `workarea/ta2-rc2-readback-preflight/20261122T005713Z-27881`; no LISTDS/IEHLIST jobs, tape movement or scratch allocation occurred. The [investigation record](ta2-rc2-readback-device-refusal-20261121.md) and `--inspect-drive` provide only fresh display inquiries and a bounded device classification. The candidate image and accepted structural review remain unchanged. This refusal is **not a readback operation** and does not authorize a mount or JES readback.

## Design implementation update: empty drive does not block read-only DASD inquiry

The [actual device diagnosis](ta2-rc2-empty-drive-readonly-preflight-20261121.md) confirms original and fresh Hercules 0480 EMPTY, MVS 480 O-NRD. A read-only preflight revision allows consistent empty or exact mounted states and keeps the existing new-target LISTDS/VTOC inquiries unchanged. It does not authorize a mount, scratch allocation, or a readback job. The accepted tape remains structurally qualified and immutable.

## Owner-reported VTOC/catalog acceptance and subsequent gated execution code

The owner ran the revised empty-drive-tolerant preflight and reported **RC=0**: **JOBS 9340/9341** checked the 21 absent targets and IEHLIST reported **15,335 free tracks** on `TSO002`. Private SHA256SUMS evidence is `workarea/ta2-rc2-readback-preflight/20261122T010923Z-28068`. The [new readback runner implementation](ta2-rc2-readback-preflight-pass-and-one-shot-implementation-20261121.md) reuses this accepted plan and exact JOB-less JCL hash `226819ef3702234a1367c7a7df96399cf9fcaf32d99152061db1df98fed12e73`, and is independently gated behind a **missing** owner execution-approval file. No MVS tape mount or DASD restore is authorized by this documentation update.
