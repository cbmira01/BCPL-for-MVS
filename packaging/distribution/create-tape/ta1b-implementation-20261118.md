# TA.1 Track B - approved load-library mechanics implementation checkpoint

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.1 - Multi-Dataset Tape Mechanics  
**Decision:** Track B design approved by owner on 18 November 2026  
**Implementation state:** Static JCL, generated-job contract and read-only MVS preflight ready; **no Track B media operation authorized or performed**.

## Exact identities and transfer contract

- Read-only MVS source: `HERC02.BCPL.MR10KIT.LOAD(ICINT19)` (PO/U/0/6144).
- Future virgin scratch image: `mvs-state/tape/bcpl-ta1-b-20261117-01.aws`, proposed distinct VOLSER `BTA102`; Hercules `0480`, MVS `480`.
- Tape logical dataset 1: `BCPL.BT0001`, `LABEL=(1,SL)`, **uncataloged** on distinct `BTA102` volume. This is a scratch fixture, *not* a candidate distribution bootstrap.
- Future **new** restored DASD load-library PDS: `HERC02.BCPL.TA1B.LOAD`, PO/U/0/6144, with `ICINT19`; only this scratch DASD PDS is to be cataloged.

Tracked, JOB-card-free JCL: `jcl/TA1BWRIT.jcl` uses IEBCOPY `COPY` plus `SELECT MEMBER=(ICINT19)` from read-only load library to a NEW/KEEP tape dataset; the output sequential IEBCOPY unload DD does not falsely claim PO/U/6144. `jcl/TA1BREST.jcl` reads that SL dataset by explicit unit/VOLSER/sequence to a NEW/CATLG scratch DASD library. Neither job touches BTA101 or an existing production load-library member.

`scripts/ta1b-contract` verifies the fixed JCL/dataset/disposition identities and 80-column cards. Its `go_body` extracts only the approved eight-case steps `SSYNI`, `STRNI`, `SCGI`, `SBLIBI`, `SICLIB`, `C01A`, `G01A`, `R01` from the existing pinned `mr10-kit-compiler/jcl/run-regression-tests.jcl` Git blob `28abf582b286401f483f1c11fcd63e303764f75e`, invoking the already accepted TA.0 `canonical_steps` extraction. It changes only the three STEPLIB DD references from the development load PDS to `HERC02.BCPL.TA1B.LOAD`. It does not change canonical MRREGRES or expected `RP:`/interpreted `CODE=` records. The same helper generates read-only IEHLIST FORMAT jobs for source and restored load directories after obtaining their actual DASD VOLSERs.

`scripts/ta1b-preflight` performs read-only static validation by default. With `--live`, it uses existing `dspal` TSO LISTDS inquiries for source DCB/member and absent scratch-target/catalog entry; Hercules `hetmap`, Docker tape binding and console device/MVS status inquiries check current scratch image/VOLSER uniqueness and unit state. Results remain private under `workarea/ta1b-operations/`. It **never** initializes, mounts, writes/restores, runs ICINT19 or automatically displaces a mounted tape. A successful preflight is not evidence of a completed tape transfer.

## MVS proof still required (separate stateful authorization)

1. Inspect and accept live `--live` read-only preflight. Do not use a VOLSER already found on any inspected tape; if 0480 is occupied, stop before any mount.
2. Separately authorize fresh `hetinit -d -i` on the unused BTA102 filename, its mount and exactly one `TA1BWRIT` job. Capture MVS JES RC/IEBCOPY messages and Hercules VOL/HDR/EOF/filemarks and image SHA-256; **never retry** uncertain writes.
3. Separately authorize conditional remount of the *same* image and `TA1BREST` to a previously absent DASD PDS. Verify actual PO/U/0/6144 source/restored DCBs and IEHLIST FORMAT directory metadata (ICINT19 entry, nonalias attributes). Do not treat directory matching as byte identity.
4. Separately authorize the canonical eight-step `TA1BGO` execution from the restored STEPLIB. Confirm each stage IEBGENER/ICINT19 RC=0000, appropriate IEF142I, interpreted `CODE=0`, and the literal golden `RP: SCALAR 17 42` and `RP: VECTOR 5 10 15 20`. Do not use IEBCOMPR for load modules.
5. Compare final AWS SHA-256 with the post-write hash and preserve original MVS/Hercules evidence. Only then consider Track B qualified acceptance and TA.1 formal closure; no release or installer acceptance follows automatically.

## Offline implementation tests

In the assistant's isolated project workspace, **44/44** dedicated synthetic and negative tests passed. Tests exercise wrong VOLSER/label/DSN/DCB/SELECT, tape-catalog attempts, GO-job STEPLIB pinning, foreign IEHLIST targets, malformed input, symlinks, existing-image collisions, catalog ambiguity, unit status, and non-shell read-only subprocess capture. The actual GitHub `MRREGRES` blob and its eight selected steps/three STEPLIB replacements were also independently inspected; all derived cards remain within 80 columns. **No MVS, Hercules mount, tape initialization, ICINT19 execution, or real IEBCOPY was performed by the assistant.**

## Subsequent live read-only preflight and producer checkpoint (18 November 2026)

The owner separately ran the committed live read-only preflight on
`eb0a26e489255e43a1bdc5089589dc53fa8347a0` and reported PASS.
Source `MR10_LOAD(ICINT19)` is PO/U/0/6144 on `TSO003`; BTA102
was absent from all four inspected existing images and proposed filename,
Hercules 0480 was empty, and the tape DSN/new DASD target were absent
in the catalog. The full private evidence remains in
`workarea/ta1b-operations/BTA102-readonly-20261118T185240Z-7885/`
on the owner's checkout, not the assistant workspace.

A new guarded `scripts/run-ta1-track-b-write` is prepared for a
**separately authorized** one-shot `hetinit -d -i`, mount at 0480,
and exactly one `TA1BWRIT` IEBCOPY job. It performs fresh live checks
twice, refuses an occupied/nonready unit, requires source VOLSER TSO003,
uses exclusive-create no-overwrite/no-retry markers, and saves JES and
Hercules label/filemark evidence plus image SHA-256. It never restores,
runs the ICINT19 GO, or catalogs the tape dataset. **27/27** additional
offline synthetic tests PASS; no live write has been executed.
See [the bounded live preflight and write-stage gate](ta1b-readonly-preflight-and-write-gate-20261118.md)
for exact scope. Prior statements describing preflight as pending are
historical; Track B remains NOT YET ACCEPTED.

## Actual one-shot unload and guarded restore preparation (18 November 2026)

Owner-reported live MVS/Hercules result on
`702617a30c765df06815bcf9c028930dfa3d91c8`:
`TA1BWRIT` JOB 9120, `UNLOAD IEBCOPY RC=0000`, physical
AWS block counts `3,8,2,0`, preserved image SHA-256
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
The subsequent `scripts/run-ta1-track-b-restore` is **not a second
writer**: default operation performs read-only MVS preflight and
saved receipt/SHA validation; separately authorized `--run` may
conditionally mount the exact existing BTA102 and submit only the
fixed `TA1BREST.jcl` into a new `HERC02.BCPL.TA1B.LOAD`.
It never initializes, overwrites, seeks, catalogs tape or executes GO.
26 synthetic/negative tests PASS. See
[write evidence and readback design](ta1b-write-evidence-and-readback-preparation-20261118.md).
