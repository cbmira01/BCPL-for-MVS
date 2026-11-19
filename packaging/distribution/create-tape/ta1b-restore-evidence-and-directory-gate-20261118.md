# TA.1 — Track B actual MVS IEBCOPY restoration and IEHLIST comparison preparation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.1 — Multi-Dataset Tape Mechanics  
**Date:** 18 November 2026 local / 19 November 2026 UTC  
**Status:** **Independent BTA102 unload and restore PASS (qualified)**. Directory metadata and restored executable GO pending.

## Real MVS job 9136 — owner-provided evidence

On GitHub `main` `b99395e19dcd3264351c753ce285b035c9a5c008`,
the owner explicitly confirmed `RESTORE BTA102 ICINT19` and
`SUBMIT TA1BREST BTA102`. The guarded runner reported:

| Item | Owner-provided result |
| --- | --- |
| Tape read | Original uncataloged `BCPL.BT0001` SL data set, BTA102 |
| MVS job / utility | `TA1BREST` **JOB 9136**, IEBCOPY **RESTORE RC=0000** |
| New DASD target | `HERC02.BCPL.TA1B.LOAD` (cataloged load-library PDS only) |
| Restored load member | `ICINT19` |
| Verified target DCB | `DSORG=PO,RECFM=U,LRECL=0,BLKSIZE=6144` |
| Restored DASD volume | `TSO002` |
| Original AWS SHA-256 | `c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210` (unchanged) |
| JES/private evidence | `workarea/ta1b-operations/BTA102-track-b-restore-20261119T021135Z-10863/` |

The assistant reviewed the Git-controlled one-shot runner and the
owner-provided terminal evidence, not the full ignored raw JES report.
The restored target is **separate** from the original read-only
`HERC02.BCPL.MR10KIT.LOAD` on `TSO003`; the original source PDS
and BTA102 image were not overwritten. These data support successful
IEBCOPY and MVS catalog/DCB verification, not module byte equality
or successful native execution.

## Next source-versus-restored MVS directory check

A new `scripts/run-ta1-track-b-directory` verifies exact
source `MR10_LOAD(ICINT19)` on **TSO003** and restored
`HERC02.BCPL.TA1B.LOAD(ICINT19)` on **TSO002**, both PO/U/0/6144.
Default invocation is **read-only MVS inquiry**: checks the original
JOB 9136 receipt, BTA102 AWS SHA, source/target `dspal stat/ls`,
one-member inventory, Git-pinned JCL generator and main-branch
source integrity. It does not submit IEHLIST jobs by default.

After a **separate explicit owner authorization**, `--run`
would perform two live IEHLIST `LISTPDS ... FORMAT` jobs:
`TA1BSRC` for TSO003 and `TA1BDST` for TSO002.
Each library DD is `DISP=SHR`. The runner requires both
IEHLIST steps and IEF142I at RC=0000, extracts the nonalias
`ICINT19` row from actual formatted SYSPRINT, and demands
source/restored entry point **000000** and attributes **02E2**.
The accepted TA.0 JOB 9060 source directory is a baseline, not
a substitute for *this* comparison.

The code refuses unknown/duplicate member entries, changed DASD
VOLSER/DCB, missing/modified original receipts, an altered AWS image,
wrong IEHLIST directory volume, or an existing one-shot marker.
Its marker is durable before submission; no automatic retry or
resubmission of a partially completed pair is allowed.
Evidence is retained privately under `workarea/ta1b-operations/`.
No `TA1BREST` rerun, tape initialization/remount, DASD modification
or executable GO occurs in this stage.

## Validation and acceptance limit

**35/35 isolated tests PASS in assistant-controlled workspace**:
27 extended synthetic/refusal cases and 8 tracked contract tests.
The committed script and tracked test module Git blobs match
their locally tested content. The two live IEHLIST jobs have
**not** yet been executed or authorized by this record.

Matching directory entry/attributes demonstrate directory-level
preservation, **not load-module byte identity or execution**.
The final Track B evidence still requires actual execution of the
canonical eight-step MR10 scalar/vector case from the restored
`HERC02.BCPL.TA1B.LOAD` `STEPLIB`, under its own explicit
authorization. TA.1 stays **IN PROGRESS**.

## Subsequent actual MVS read-only directory preflight (18 November 2026 EST)

The owner invoked `run-ta1-track-b-directory` without `--run`
from GitHub `main` `58f98db10dd5b790ea52c488070c6de2a98b98d5`.
The tool reported PASS for source TSO003 and restored TSO002,
both PO/U/0/6144, with unchanged BTA102 hash and JOB 9136
receipt. Private evidence:
`workarea/ta1b-operations/BTA102-track-b-directory-20261119T023717Z-11735/`.
The live check did **not** submit either IEHLIST job or execute
`ICINT19` and therefore does not establish directory metadata
identity. See [the independent preflight record](ta1b-directory-readonly-preflight-20261118.md).
