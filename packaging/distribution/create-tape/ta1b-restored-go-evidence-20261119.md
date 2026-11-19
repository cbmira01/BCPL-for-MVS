# TA.1 — Track B actual MVS restored ICINT19 GO evidence

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** TA.1 — Multi-Dataset Tape Mechanics  
**Date:** 19 November 2026, approximately 12:10 UTC / 07:10 EST  
**Disposition:** **Track B restored executable-use PASS (qualified).**

## Actual owner-reported JES/BCPL result

The owner ran exactly the separately authorized one-shot MVS operation
at GitHub `main` `199ea8536bb0ece10ad04c0a32020a18335b60b5`:

    packaging/distribution/create-tape/scripts/run-ta1-track-b-go --run

The runner repeated its read-only MVS and saved-IEHLIST guard, and
the owner supplied exact typed approval
`RUN RESTORED ICINT19 SCALVEC`. Its terminal result was:

    TA1BGO MVS JOB 9165: 8 steps RC=0000; 3 restored ICINT19 calls; scalar/vector RP PASS.
    BTA102 unchanged; executable-use PASS (qualified; not binary equality).
    Evidence: workarea/ta1b-operations/BTA102-track-b-go-20261119T121015Z-13509

The accepted canonical eight-step MRREGRES scalar/vector case
(`SSYNI`, `STRNI`, `SCGI`, `SBLIBI`, `SICLIB`,
`C01A`, `G01A`, `R01`) uses `IEBGENER` for the first five
steps and `ICINT19` for the last three. **All three `STEPLIB` DDs**
are generated from the Git-blob-pinned original MRREGRES job to
read `HERC02.BCPL.TA1B.LOAD`, the independent tape-restored
`PO/U/0/6144` load PDS on `TSO002`, rather than the
development source PDS on `TSO003`.

The runner's PASS criteria include 8 JES step RC=0000,
8 corresponding `IEF142I` confirmations, three interpreted
`CODE=0` outcomes, and exactly these golden semantic records:

    RP: SCALAR 17 42
    RP: VECTOR 5 10 15 20

The original BTA102 AWS image SHA-256 remains
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
The test uses existing `DISP=SHR` inputs and temporary `&&`
work datasets only, not a tape remount, write or new permanent PDS.

**Provenance of this evidence:** the owner's actual MVS-facing
runner output and the previously reviewed Git-controlled code;
the assistant did not separately inspect the private JES report.
The output therefore supports the bounded result validated by
the runner and does not supply independently examined raw bytes.

## Track B acceptance chain

- `TA1BWRIT` JOB 9120: IEBCOPY selected-member UNLOAD RC=0000;
  standard-label BTA102 AWS file counts `3,8,2,0`
  and immutable image identity.
- `TA1BREST` JOB 9136: independent IEBCOPY RESTORE RC=0000 to
  **new** `HERC02.BCPL.TA1B.LOAD(ICINT19)` on `TSO002`,
  `PO/U/0/6144`.
- `TA1BSRC` JOB 9151 and `TA1BDST` JOB 9152:
  independent read-only IEHLIST RC=0000, matching nonalias
  `ICINT19` entry `000000` and attributes `02E2`.
- `TA1BGO` JOB 9165: canonical eight-step restored-`STEPLIB`
  scalar/vector execution **PASS (qualified)**.

**Qualification:** IEHLIST directory equality plus successful
execution on this bounded case is not a byte-for-byte comparison
of the RECFM=U load member, nor full MR10 distribution regression.
It is the accepted TA.1 Track B *executable-use path* evidence.
See [TA.1 formal qualified acceptance candidate](../../milestones/tape-artifact-release/ta1-qualified-acceptance-candidate-20261119.md).
