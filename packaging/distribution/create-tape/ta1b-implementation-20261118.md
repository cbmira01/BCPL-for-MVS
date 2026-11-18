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
