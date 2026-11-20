# TA.2 — BT0001/BT0002 one-shot MVS staging: JOB 9317

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026  
**Status:** One-shot MVS staging **EXECUTED RC=0000** (owner-reported); independent DCB/directory review pending.

## Owner-operated MVS checkpoint

With the Git-controlled `BCPL-0.1.0-rc1` identity, existing `BC0001` reservation and the narrowly scoped one-shot staging approval, the owner executed:

```text
TA.2 BT STAGING PREFLIGHT: 2/2 absent; TSO002 free tracks 15400; six steps approved.
Submit one-shot BT0001/BT0002 staging? [y/N]: y
TA.2 BT STAGING: JOB 9317; 6/6 steps RC=0000. Directory/DCB review pending.
Private MVS evidence: workarea/ta2-bootstrap-stage-operations/20261120T132013Z-21957
```

This is an actual MVS execution result **reported by the owner**, not an assistant replay of the private raw JES evidence. The accepted scope is creation of **only**:

- `HERC02.BCPL.TA2STG.BT0001`, sequential `PS/FB/80/800`.
- `HERC02.BCPL.TA2STG.BT0002`, partitioned `PO/FB/80/800`, installer members `INSTALL`, `DATASETS`, `RELEASE`, `RESTORE`.

Both are on TSO002. The owner-reported six steps are one IEFBR14 and five IEBGENER. The old BT0003–BT0020 datasets, staged successfully in JOB 9310 and verified in JOBS 9311/9312, remain accepted. Do **not** rerun JOB 9317 or any part of prior staging; the marker is non-retryable.

## New read-only MVS DCB/directory acceptance

`scripts/ta2-bootstrap-stage-verify --live` replays the saved SHA256-sealed JOB 9317 result and permanent no-retry intent against the existing `ta2-bootstrap-stage-once.validate_job`, without resubmitting the stage job. It then issues **two consolidated read-only MVS LISTDS inquiries**, using existing `dspal-core` and `dspal-ls` interfaces:

1. `LISTDS LABEL` for both BT0001/BT0002: require TSO002 and exact `PS/FB/80/800` / `PO/FB/80/800` attributes.
2. `LISTDS MEMBERS` for BT0002: require exactly the four expected installer members, no missing, unexpected or duplicate entries.

The verifier retains MVS original reports, summaries, cursors, a verification receipt and SHA256 checksum under **new ignored repository `workarea/ta2-bootstrap-stage-verification/` evidence**. It does not print raw JES reports to the WSL terminal, write or modify the staged datasets, or touch Hercules tapes. No redundant byte-for-byte verification of trusted IBM IEBGENER/IEFBR14 is introduced.

The assistant ran **16/16 focused synthetic offline tests PASS**, including original receipt/marker validation, wrong DCB/VOLSER and directory refusal, no overwrite, protected private evidence and two consolidated read-only inquiry jobs. Python compilation passed. The GitHub-uploaded source and tests matched the locally tested Git blob SHAs. No live MVS inspection or verification-job result has yet been reported.

## Later TA.2 boundaries

If the actual new MVS directory/DCB results pass, the two missing staging inputs can be accepted alongside BT0003–BT0020. Full release production remains blocked on the canonical frozen candidate manifest's per-member rights/lineage, source/build receipts, unload DCB/evidence and strict producer gate. The new AWS `BC0001` candidate **has not been initialized, written, or authorized for media creation**. Independent tape readback, recipient installation and publication are separate acceptance stages. Trust successful established MVS utility results unless concrete anomalies arise.

**TA.2 remains IN PROGRESS; TA.0/TA.1 qualified closures unchanged.**
