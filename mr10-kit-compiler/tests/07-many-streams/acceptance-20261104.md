# MR10 development-probe acceptance — 07-many-streams

**Project:** BCPL for MVS 3.8 Reconstruction  
**Case:** `07-many-streams`  
**Date:** 4 November 2026  
**Source revision:** `6c98bcf16171bc7f4589b7af038408f42c8dc725`  
**MVS evidence:** JES JOB 9548, job name `DP048850`

Under the project owner's approval to establish the observed cases' contracts,
this result is accepted as an **initial golden-output baseline** after
independent review of the saved MVS job-summary, JES report, and ICINT program log.

- JES job summary: **SUCCESS**, highest return code `0000`.
- All **10** executed JES steps returned `RC=0000`.
- All **3** interpreted compiler, generator and execution phases ended `CODE=0`.
- Final interpreted program output matched the exact records in
  [`07-many-streams.expected`](07-many-streams.expected).

Evidence remains in the operator-local workarea:
`workarea/mr10-probes/20261104T190013Z-28850-2_n4npqv/`.
The original runner returned `OBSERVED` rather than PASS because the
golden oracle was not yet accepted. This historical review does **not**
establish that the revised multi-case acceptance runner has been independently
verified by a fresh MVS run.

The remaining eleven historical development-probe contracts are UNVERIFIED.
The separate 12-case MR10 Regression Panel is unchanged.
