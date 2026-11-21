# TA.2 — Owner-authorized private BC0002 candidate production

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**State:** **One private candidate-media operation approved, execution pending.**

## Owner decision and exact operational boundary

After successful owner-operated read-only Hercules/MVS preflight, the owner approved the previously proposed **single private `BCPL-0.1.0-rc2` candidate build** using:

- Existing accepted `HERC02.BCPL.TA2STG.BT0001`–`BT0021` on TSO002, opened read-only;
- Reserved volume serial `BC0002`, Hercules device `0480`, new image `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`;
- Exactly **one guarded `TA2RC2WR` JES submission**, generated from the existing manifest: **one IEBGENER and 20 IEBCOPY steps**, 21 ordered standard-labeled tape datasets, 146 selected PDS member controls;
- Interactive confirmation `INIT MOUNT WRITE BC0002 21` before initialization/mount, then `SUBMIT TA2RC2WR BC0002` immediately before one JES submission;
- Fresh preflight and permanent exclusive no-retry attempt marker before initializing a new image.

The owner explicitly **did not approve** release publication, source redistribution-rights clearance, rewriting historical source, restaging accepted PDS inputs, tape restoration, clean-target installation, automatic retries or recovery writes. No actual AWS creation/JES write is asserted by this authorization record.

The exact approved 399-line, 12,151-byte JOB-less JCL body has SHA-256:

`85eca6f3e1e83c2d0e476f24870a20664bde2a50e2de8653606bfa351af54b4f`

The SHA was computed independently from the canonical `ta2-offline.render_write_jcl` contract and the unchanged `BCPL-0.1.0-rc2.yaml` selected members and cross-checked in the assistant Python workspace. The commit includes the exact, separate `ta2-rc2-media-write-approval.json` file required by the existing `scripts/ta2-rc2-produce-once` hard gate. The producer rejects differing JCL bytes or approval metadata before starting the MVS/media operation.

## Actual MVS checkpoint and saved evidence

The owner reported:

```text
TA.2 RC2 DRIVE PREFLIGHT PASS: Hercules 0480 empty; MVS 480 O-NRD.
Private evidence: workarea/ta2-rc2-media-preflight/20261121T133703Z-25915
No media, MVS datasets, or JES jobs changed; AWS production still unauthorized.
TA.2 RC2 drive preflight RC=0
```

This actual read-only PASS is accepted as evidence of the device's state **at that instant**. The guarded writer repeats live checks, catalog absence and VOLSER/image collision investigation immediately before any state-changing operation; a stale PASS cannot authorize an unsafe new mount.

Accepted staging receipts remain under ignored `workarea/`: JOBS 9310/9311/9312 for BT0003–BT0020; 9317/9318/9319 for BT0001/BT0002; 9335 and later independent LISTDS for BT0021. They are not rerun merely to certify IBM utilities again.

## Implementation and test gate

The existing guarded `ta2-rc2-produce-once --run` performs its preflight, refuses an existing `BC0002` medium or permanent attempt marker, creates the marker *before* an exclusive new AWS image, executes HETINIT and mount, submits one authenticated MVS job only after a second explicit confirmation, verifies the full 21-step JES and IEF142I results, checks independent HETMAP standard labels/filemarks, and records the media SHA-256 under private workarea. It never catalogs tape aliases, retries, unmounts, restores or publishes the tape.

This approved update adds an **SHA256SUMS seal** to successful and halted private operation evidence; no existing saved evidence is altered. The assistant workspace passed **62/62 focused offline tests**, including two new seal checks, and Python syntax verification. A synthetic test PASS is **not** proof of 21-dataset MVS write execution.

After the owner's single run, inspect the original MVS/JES evidence, 21 SL dataset identities, physical-file layout, and output SHA. If anything is incomplete or ambiguous, preserve the image/mount/attempt marker; **never rerun the one-shot producer**. Independent tape readback/restore will require its own approved operation under the existing milestone structure.

**TA.2 — Manifest-Driven Tape Producer remains IN PROGRESS.**
