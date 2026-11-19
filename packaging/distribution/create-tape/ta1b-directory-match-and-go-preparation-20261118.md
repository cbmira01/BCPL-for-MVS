# TA.1 — Track B actual directory match and restored ICINT19 GO preflight

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.1 — Multi-Dataset Tape Mechanics  
**Date:** 18 November 2026 EST / 19 November 2026 UTC  
**Status:** SOURCE/RESTORED IEHLIST **PASS (qualified)**; restored GO **NOT EXECUTED**.

## Owner-provided actual MVS comparison

The owner ran the approved one-shot `run-ta1-track-b-directory --run`
at GitHub `main` `a296b8b60d1c3459a1c263ea4c4487632644277b`
and confirmed `COMPARE ICINT19 DIRECTORIES`.

| Actual MVS evidence | Original load PDS | Restored load PDS |
| --- | --- | --- |
| IEHLIST program | `TA1BSRC` JOB 9151 | `TA1BDST` JOB 9152 |
| MVS DASD VOLSER | `TSO003` | `TSO002` |
| IEHLIST step | `DIRLIST RC=0000` | `DIRLIST RC=0000` |
| PDS member | `ICINT19` | `ICINT19` |
| Directory entry point | `000000` | `000000` |
| Directory attrs | `02E2` | `02E2` |

The runner reported `TA.1B SOURCE/RESTORED ICINT19 DIRECTORY MATCH (IEHLIST FORMAT only)`
and original BTA102 SHA-256 unchanged:
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.

Original owner-local private JES/IEHLIST reports and typed comparison:
`workarea/ta1b-operations/BTA102-track-b-directory-20261119T024927Z-11906/`.

These actual results demonstrate MVS directory-level consistency,
**not** load-module byte identity or restored `ICINT19`
executable behavior. The assistant has not separately read the
ignored raw JES reports, only the owner output and committed parser.

## Prepared next stage — one restored-STEPLIB GO

The tracked `scripts/run-ta1-track-b-go` defaults to read-only
MVS catalog and saved-evidence validation:
- Re-read both actual IEHLIST 9151/9152 reports, RC and IEF142I;
  verify the exact source/restored directory entries and attributes
  against saved `directory-comparison.json`, and verify its durable
  completed one-shot marker.
- Recheck the actual independent IEBCOPY `TA1BREST` JOB 9136
  receipt, original AWS SHA, source TSO003 and restored TSO002 DCBs
  `PO/U/0/6144` and one-member inventories.
- Generate exactly the pinned canonical eight-step MRREGRES
  `SCALVEC` case: `SSYNI`, `STRNI`, `SCGI`, `SBLIBI`,
  `SICLIB` (IEBGENER), `C01A`, `G01A`, `R01` (ICINT19).
  Verify all three interpreter `STEPLIB` DDs select
  `HERC02.BCPL.TA1B.LOAD`, with no source load-library `STEPLIB`.
  All generated work outputs remain temporary `&&` datasets.

The GO operation is *not* part of the directory approval.
**Only after distinct owner authorization**, `--run` repeats
preflight and typed confirmation `RUN RESTORED ICINT19 SCALVEC`,
writes a durable no-retry marker, and submits one authenticated
`TA1BGO` MVS job. It requires all 8 JES steps RC=0000,
8 successful IEF142I confirmations, exactly 3 restored ICINT19
invocations, interpreted CODE=0 and golden `RP: SCALAR 17 42`,
`RP: VECTOR 5 10 15 20`. On ambiguity the evidence and marker
are retained, and no resubmission occurs.

The runner does not initialize, mount, read or write tape; does not
change either permanent load PDS; never retries a JES submission.
No executable-use PASS is claimed without actual MVS output.

**Assistant workspace tests:** 32/32 isolated synthetic/refusal
tests PASS, plus Python source and test bytecode compilation.
The Git blob hashes of both tracked files match the tested bytes.
TA.1 remains **IN PROGRESS**, and GO authorization and execution
remain open.

## Subsequent live restored-GO read-only preflight PASS — 19 November 2026

The owner ran `scripts/run-ta1-track-b-go` without `--run`
on GitHub `main` `acae8bd36b222bc4e3ef7ac5bee57ea482c1dcf3`.
The actual MVS-facing preflight reported valid IEHLIST JOBS 9151/9152,
matching ICINT19 entry `000000`, attrs `02E2`, source TSO003,
restored TSO002, matching PO/U/0/6144 and preserved BTA102 SHA-256.
It executed **NO** GO JES job and made **NO** MVS or tape changes.
Evidence: `workarea/ta1b-operations/BTA102-track-b-go-20261119T114903Z-13321/`.
The separate one-shot `TA1BGO` execution authorization remains pending.
See [live read-only GO preflight receipt](ta1b-go-readonly-preflight-20261119.md).
