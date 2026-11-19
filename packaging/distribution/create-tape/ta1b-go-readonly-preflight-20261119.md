# TA.1 — Track B restored ICINT19 GO: live read-only preflight PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.1 — Multi-Dataset Tape Mechanics  
**Date:** 19 November 2026, 06:49 EST / 11:49 UTC  
**Status:** RESTORED-GO READ-ONLY PREFLIGHT **PASS**. **TA1BGO not authorized or executed.**

## Actual MVS-facing owner report

On GitHub `main` at
`acae8bd36b222bc4e3ef7ac5bee57ea482c1dcf3`,
the owner invoked the committed
`packaging/distribution/create-tape/scripts/run-ta1-track-b-go`
**without `--run`** and reported exactly:

    TA.1B RESTORED GO READ-ONLY PREFLIGHT PASS: IEHLIST jobs 9151/9152, entry 000000 attrs 02E2.
    MVS source TSO003 / restored TSO002 PO/U/0/6144; original BTA102 SHA-256 preserved.
    No ICINT19 GO JES submission; no MVS dataset or tape change.
    Evidence: workarea/ta1b-operations/BTA102-track-b-go-20261119T114903Z-13321

The checked source is `HERC02.BCPL.MR10KIT.LOAD(ICINT19)`
on `TSO003`; the independent restored target is
`HERC02.BCPL.TA1B.LOAD(ICINT19)` on `TSO002`. Both are
`PO/U/0/6144`. Original source/restored IEHLIST jobs 9151/9152
have matching directory entry `000000` and attributes `02E2`;
the job 9136 restore receipt is required by the runner. The original
AWS image SHA-256 remains
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.

This is evidence of a live read-only MVS inquiry and authenticated
saved-receipt validation, not fresh executable-use evidence.
The assistant reviewed the Git-controlled runner and this owner
terminal output but has not separately inspected the ignored raw
evidence files.

## Next distinct authorization and validation

The source-controlled `scripts/run-ta1-track-b-go --run` would,
only after **separate explicit owner authorization**, repeat the
live checks, require a TTY confirmation
`RUN RESTORED ICINT19 SCALVEC`, create an exclusive no-retry marker,
and submit exactly one `TA1BGO` JES job. The eight pinned MRREGRES
scalar/vector steps are `SSYNI`, `STRNI`, `SCGI`,
`SBLIBI`, `SICLIB` (IEBGENER), then `C01A`, `G01A`,
`R01` (ICINT19). All three interpreter `STEPLIB` DDs
reference **only** restored `HERC02.BCPL.TA1B.LOAD`; other
inputs are read-only and outputs are temporary `&&` datasets.

The runner requires all eight steps RC=0000, eight matching
`IEF142I` successful steps, three interpreted CODE=0 results,
and exact `RP: SCALAR 17 42` and
`RP: VECTOR 5 10 15 20` output. Any unexpected or
ambiguous result halts the runner without automatic retry.
Neither the tape nor either permanent load library is changed.

**Static source review:** 14/14 key safety invariants PASS for
the already committed runner. The prior 32/32 isolated tests PASS,
but have not been rerun at this checkpoint; no new implementation
was required.

**Acceptance boundary:** The GO has not been executed; no
restored executable-use PASS, binary byte equivalence or
TA.1 closure can be claimed yet.

## Subsequent owner authorization of the one-shot GO (19 November 2026)

The owner approved exactly one `TA1BGO` JES submission with the
canonical eight-step MRREGRES scalar/vector case 01, selecting the
independently restored `HERC02.BCPL.TA1B.LOAD` in each of the three
`STEPLIB` DDs. The unchanged runner was reviewed and retained.
No GO execution was yet observed at this authorization checkpoint.
See [GO authorization and execution boundary](ta1b-go-submission-authorization-20261119.md).
