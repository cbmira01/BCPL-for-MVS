# TA.1 — Track B authorization for one restored-STEPLIB ICINT19 GO

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.1 — Multi-Dataset Tape Mechanics  
**Authorized:** 19 November 2026  
**Status:** **One TA1BGO authorized; no JES execution result yet.**

## Authority and approved scope

Following the owner-reported live read-only preflight PASS on
GitHub `main` `acae8bd36b222bc4e3ef7ac5bee57ea482c1dcf3`,
the owner explicitly approved **one** guarded `TA1BGO`
JES submission using the independent restored
`HERC02.BCPL.TA1B.LOAD(ICINT19)` on `TSO002`.

The job is pinned to the original canonical MRREGRES scalar/vector
case 01, with exactly eight ordered steps:
`SSYNI`, `STRNI`, `SCGI`, `SBLIBI`, `SICLIB`
(IEBGENER), and `C01A`, `G01A`, `R01` (ICINT19).
All three `STEPLIB` DDs must use the restored
`HERC02.BCPL.TA1B.LOAD` rather than the source
`HERC02.BCPL.MR10KIT.LOAD`.
Existing input datasets remain `DISP=SHR`; all created
MVS work datasets are temporary `&&` allocations.

The runner requires eight JES step return codes `0000`,
eight matching `IEF142I` confirmations, three successful
ICINT19 interpreted CODE values, and the exact semantic output
`RP: SCALAR 17 42` and `RP: VECTOR 5 10 15 20`.
No tape mount, initialization, copy or remount; no permanent
source/restored DASD dataset modifications; no installation,
publication or further tests are included.

## One-shot safety gate

The committed `packaging/distribution/create-tape/scripts/run-ta1-track-b-go`
was re-reviewed at GitHub `main`
`e31307efda3abe92334556840a2c2a4bf5988bfa`.
It requires two live verification passes of the completed
IEHLIST JOBS 9151/9152, independent IEBCOPY restore JOB 9136,
both load-library attributes/volumes, unchanged BTA102 AWS SHA,
pinned canonical JCL and exact restored STEPLIB bindings.
It then requires the interactive confirmation token
`RUN RESTORED ICINT19 SCALVEC` before writing a durable
`BTA102-track-b-go-attempt.json` marker and submitting one JES job.
A failed, incomplete or ambiguous submission is **never**
automatically retried; the marker and raw MVS evidence remain
preserved under `workarea/ta1b-operations/`.

The previous source/test package passed 32/32 isolated offline
tests. An additional 19/19 source-level review invariants PASS
on this unchanged commit; these are checks, **not actual MVS
execution**. No change to the reviewed runner is necessary.

## Remaining acceptance decision

**One TA1BGO is now authorized but has not yet been observed.**
Do not classify Track B executable-use as PASS or close TA.1
until actual JES/ICINT19 results are reviewed. A successful
execution would establish restored load-module behavior for
this accepted bounded test, not binary byte-for-byte identity
or finished release acceptance.

## Subsequent authorized actual MVS result (19 November 2026)

After the approval recorded above, the owner ran the guarded
`run-ta1-track-b-go --run` and confirmed
`RUN RESTORED ICINT19 SCALVEC`. MVS `TA1BGO`
**JOB 9165** returned 8 steps RC=0000, 3 restored `ICINT19`
calls and scalar/vector `RP:` PASS. The original AWS checksum
remained unchanged. Evidence:
`workarea/ta1b-operations/BTA102-track-b-go-20261119T121015Z-13509/`.
The earlier authorization-status heading is historical;
the one-shot GO is now **PASS (qualified)**, not merely approved.
See [actual GO evidence](ta1b-restored-go-evidence-20261119.md).
