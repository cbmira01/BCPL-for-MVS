# TA.1 Track B — actual BTA102 write receipt and independent restore preparation

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone / march:** Tape artifact release / TA.1 — Multi-Dataset Tape Mechanics
**Date:** 18 November 2026 (23:52 UTC / 18:52 EST)
**Status:** Selected-member BTA102 tape WRITE **PASS (qualified)**. Independent restore and GO **NOT EXECUTED**.

## Owner-reported real MVS/Hercules execution

The owner fast-forwarded GitHub `main` to
`702617a30c765df06815bcf9c028930dfa3d91c8` and invoked
`packaging/distribution/create-tape/scripts/run-ta1-track-b-write --run`.
After a fresh read-only PASS, the owner confirmed both
`INIT MOUNT WRITE BTA102` and `SUBMIT TA1BWRIT BTA102`.
The runner reported the following actual guest and host results:

| Evidence item | Owner-reported result |
| --- | --- |
| Tape AWS image | `mvs-state/tape/bcpl-ta1-b-20261117-01.aws` |
| Distinct scratch VOLSER | `BTA102` |
| Device | Hercules 0480 / MVS UNIT=480 |
| Source | `HERC02.BCPL.MR10KIT.LOAD(ICINT19)` PO/U/0/6144 |
| Logical tape dataset | `BCPL.BT0001`, first SL dataset, **uncataloged** |
| MVS job | `TA1BWRIT` JOB **9120** |
| IEBCOPY step | `UNLOAD` RC=0000 |
| Hercules physical-file block counts | **3, 8, 2, 0** |
| Original SHA-256 | `c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210` |

The runner saved original private JES/job summary and SYSPRINT,
`hetmap -l/-f/-a`, device reports, one-shot attempt marker, and
checksum under:

`workarea/ta1b-operations/BTA102-track-b-write-20261118T235204Z-9548/`

The assistant has reviewed the authoritative Git-controlled runner
and the owner's terminal receipt. The complete private contents
of that ignored evidence folder have **not** been separately read
by the assistant; do not invent additional IEBCOPY SYSPRINT
messages or imply byte-for-byte restored equivalence.

The physical-file layout is compatible with one complete
standard-labeled logical tape dataset: VOL1/HDR1/HDR2 (3 blocks),
IEBCOPY unload data (8), EOF1/EOF2 (2), terminal empty file (0).
This is one **logical MVS dataset**, not four cataloged datasets.

## Readback design, verification and safety

The approved original Track B design calls for restore to
`HERC02.BCPL.TA1B.LOAD`, cataloged **on DASD only**,
with `DSORG=PO,RECFM=U,LRECL=0,BLKSIZE=6144`.
`TA1BREST.jcl` was previously pinned and validated; it reads the
uncataloged BTA102 tape DSN by explicit VOL=SER and LABEL=(1,SL).

New tracked `scripts/run-ta1-track-b-restore` defaults to **read-only**
live preflight, verifying the JOB 9120 write summary, durable original
attempt receipt, label/filemark layout, original AWS hash, all
other inspected media VOLSERs, MVS source and catalog target-absence,
and Hercules 0480 state. Evidence remains under ignored
`workarea/ta1b-operations/`; no restored load PDS is created by
default.

Only after **separate explicit owner approval** can `--run`:
1. repeat live safety checks and require a typed restore confirmation;
2. atomically record a no-retry restore attempt before any remount;
3. conditionally mount ONLY the original BTA102 image if the device
   remains empty and available; never displace other media;
4. submit the fixed `TA1BREST` IEBCOPY job once, with the project
   authenticated JOB card in memory, retaining JES evidence privately;
5. require MVS IEBCOPY RC=0000, verify restored PO/U/0/6144 DCB and
   exactly one `ICINT19` member, and rehash the untouched AWS image.

The independent *source-versus-restored IEHLIST FORMAT* directory
verification and actual eight-step MRREGRES scalar/vector
`ICINT19` execution from **restored STEPLIB** remain further,
separately authorized stages. IEBCOMPR must not be claimed as
a safe binary load-module comparison or as acceptance evidence.

## Offline tests and acceptance boundary

**26/26 isolated synthetic and refusal tests PASS** using the assistant
workspace under `BCPL-for-MVS/workarea/ta1b-restore-review/`.
Tests cover saved receipt, AWS checksum, symlinks, wrong filemarks,
foreign/same-basename media, conditional mount, original source
attempt, one-time marker, source/destination attributes, default
no-state-change, denied confirmation, double preflight and mocked
single submission. The exact tested script and test module Git
blob checksums were compared before promotion.

Track B write is **PASS (qualified)**; TA.1 remains **IN PROGRESS**.
No independent BTA102 restore, directory metadata comparison,
restored executable use, product tape release, or recipient install
has been accepted.

## Subsequent live restore preflight PASS (18 November 2026, 19:24 EST)

The owner ran the committed `run-ta1-track-b-restore` with its default
read-only mode on GitHub `main`
`52c128ca4dac2b82549114976f4f4eee807aa9d6`. The runner
verified the original BTA102 JOB 9120 receipt and SHA-256, found
Hercules 0480 empty and the intended new DASD load PDS still absent,
and returned `TA.1 Track B restore preflight PASS`. Its evidence is
under `workarea/ta1b-operations/BTA102-track-b-restore-20261119T002435Z-10407/`.
The run performed NO tape mount, new DASD PDS allocation, restore,
IEHLIST directory comparison or restored ICINT19 GO. Those stages
remain pending separate authorization and actual MVS evidence.
See [the qualified read-only result](ta1b-restore-readonly-preflight-20261118.md).

## BTA102 independent MVS restore completed (18 November 2026)

The owner executed the separately authorized `TA1BREST` one-shot
restore at GitHub main `b99395e19dcd3264351c753ce285b035c9a5c008`.
MVS JOB **9136** completed `RESTORE IEBCOPY RC=0000` and the
restored load library `HERC02.BCPL.TA1B.LOAD(ICINT19)` was
verified on **TSO002** with `PO/U/0/6144`. BTA102 retained its
original SHA-256. Private evidence:
`workarea/ta1b-operations/BTA102-track-b-restore-20261119T021135Z-10863/`.
Prior statements that restoration was pending are historical.
IEHLIST directory comparison and actual restored ICINT19 GO remain
pending; see [directory verification preparation](ta1b-restore-evidence-and-directory-gate-20261118.md).
