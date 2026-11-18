# TA.1 Track B — live read-only preflight and guarded scratch write preparation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.1 — Multi-Dataset Tape Mechanics  
**Date:** 18 November 2026 (local); reported evidence folder 18:52 UTC  
**State:** Read-only live preflight **PASS (operator-reported)**; producer code staged. **No stateful tape or new DASD operation authorized or performed.**

## Owner-supplied live evidence

The owner fast-forwarded to GitHub `main` at
`eb0a26e489255e43a1bdc5089589dc53fa8347a0` and executed
`packaging/distribution/create-tape/scripts/ta1b-preflight --live`.
The owner-provided output confirms:

- `MR10_LOAD` (`HERC02.BCPL.MR10KIT.LOAD`): `DSORG=PO`, `RECFM=U`, `LRECL=0`, `BLKSIZE=6144`; only member `ICINT19`; DASD VOLSER `TSO003`.
- `BTA102` absent among **four inspected** existing AWS images, with proposed new `mvs-state/tape/bcpl-ta1-b-20261117-01.aws` path absent. This is a scoped observed inventory, not a universal reservation.
- Hercules `0:0480` **EMPTY**; MVS unit `480` reported. The preflight alone does not prove the stricter online/ready state for the moment of a future mount; the write runner checks that again.
- Uncataloged tape DSN `BCPL.BT0001` and new DASD restoration target `HERC02.BCPL.TA1B.LOAD` both absent in the catalog.
- Complete private read-only inquiry evidence retained on the owner's checkout at `workarea/ta1b-operations/BTA102-readonly-20261118T185240Z-7885/`. Raw private files were not provided to this conversation and are not asserted to have been inspected by the assistant.

**No tape image was initialized or mounted, and no TA1BWRIT, TA1BREST or TA1BGO production JCL was submitted.** The inquiry may have used the existing MVS LISTDS/JES mechanisms; that is not a Track B production operation.

## Guarded next stage: selected-member unload only

The tracked `scripts/run-ta1-track-b-write` is inert by default. Its `--run` mode is reserved for **separate explicit owner authorization** of exactly one fresh BTA102 initialization, mount at 0480, and exactly one `TA1BWRIT` IEBCOPY job. It does not restore, run ICINT19, alter existing tapes, or catalog any tape dataset.

Safety contract:

1. Revalidate pinned JCL and eight-step MRREGRES contract; git branch/clean tracked files; original MR10_LOAD member/DCB/VOLSER `TSO003`; virgin image path; no BTA102 collision among all inspected tape media; new restore target and tape DSN absent in catalog; Docker tape bind and effective UID/GID; installed `hetinit -d -i`; and an **empty, unallocated, online/ready** `0480`.
2. Require a typed exact confirmation; repeat read-only live checks immediately before any state change; atomically record a durable no-retry marker under ignored `workarea/ta1b-operations/`; exclusively create the new AWS filename so prior media cannot be overwritten.
3. Initialize the new AWS with `hetinit -d -i`, verify fresh `VOL1` serial `BTA102`, recheck idle tape unit, mount and verify its identity. Require a separate typed submission confirmation. Submit only the existing Git-controlled `TA1BWRIT` body with MVS authenticated JOB card held in memory, using the established `dspal-core.submit_and_wait` path.
4. Preserve JES job summary and report, Hercules labels and physical-file maps (`hetmap -l/-f/-a`), post-job device reports, and image SHA-256 under private ignored `workarea`. Require `UNLOAD IEBCOPY RC=0000`, exact `VOL1/HDR1/HDR2/EOF1/EOF2` for `BCPL.BT0001` sequence 0001, and four physical tape-file segments of `[3, positive data block count, 2, 0]`.
5. On any uncertain stage, stop permanently for owner review. **No automatic retry, remount, overwrite, restore, or GO.** The original source load PDS is read-only. The eventual cataloged target is a separate, later-approved DASD restore PDS.

**Local offline validation:** 27/27 synthetic/negative tests PASS for the new one-shot runner. This is **not** actual MVS unload verification. Track A remains qualified PASS. Track B and TA.1 remain IN PROGRESS. Release publication and recipient installation remain outside this experiment.
