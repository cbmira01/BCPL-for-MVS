# CO.3 — JOB 5389 output-capacity failure and corrected fixture

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle (**IN PROGRESS**)  
**Date:** 14 November 2026 (Louisville local time)  
**Tested GitHub main:** `a09e371edb3ca75c09ae8c0580ff09d0cb7f1ed0`  
**Evidence class:** OWNER-REPORTED NATIVE-MVS-FAILED; operational evidence extracted from owner-provided saved receipt summary

## Observed JES

Native JOB **5389**: ASMA, ASML, ASMM, ASMS and LKED all
**RC=0000**; GO **RC=0012**; overall JOB FAILURE/HIGHEST RC=0012.

The saved output markers are:

    MADE A1 B1 A2 B2 R1 A3 R2 B3 R3 A4 R

The final `R` is an incomplete `R4` marker, not a completed step.
`PASS` was not emitted. The runner correctly returned RC=1.

Operator-local evidence:
`workarea/co3-first-lifecycle/20261114T190836Z-v_koeeti`.

## Source-level diagnosis

The accepted [Core Runtime contract](../architecture/runtime-contract-v1.md)
documents **RC=12** for writing a non-newline character to a full
132-byte primary `BCPLIO` record. The native implementation's
`IOWRCH` uses `IOLF DC F'10'` as its record-flushing newline control
and `IOWFULL` invokes STOP(12) when the buffer is full.

The parent-chain fixture used `NEWLINE()` between `WRITES`
markers. Counting each marker and one nominal newline character:

- `MADE` through `A4`: **123** bytes;
- `CO3BCPL R` prefix: **9** additional bytes;
- cumulative output: **132** bytes, matching the failure exactly;
- full 13-marker sequence would be **147** bytes.

This alignment and RC=12 are strong evidence that `NEWLINE()` did
not cause an actual `IOWRCH` record flush during this run. The
precise compiled `BLIB NEWLINE` character-value mismatch, if any,
has not yet been established with a dedicated machine probe.
This is **not** evidence that `RESUMECO` or `CHANGECO` failed.

## Minimal next MVS probe

Replace the parent-chain fixture's 19 `NEWLINE()` calls with
`WRCH(10)` (historical G!14), matching the native I/O control code.
Leave all 13 marker strings, arithmetic assertions, coroutine
transitions, separate compiler/object linkage and the strict JES/GO
oracle unchanged.

The new isolated source check asserts that the exact 132-byte overrun
is explained by the original marker lengths, and that the corrected
fixture uses the explicit `WRCH(10)` call. Successful offline checks
are **not** native GO evidence. A fresh MVS run must independently
demonstrate all 13 markers and GO RC=0000.

Investigate `BLIB NEWLINE()` versus native `WRCH(10)` separately;
do not silently promote any undocumented newline ABI or alter
installed Core Runtime/BLIB objects.

**Current disposition:** JOB 5389 remains FAIL; first-slice
JOBS 5384–5386 retain their independent PASS status; CO.3 remains
IN PROGRESS, CO.4–CO.5 NOT STARTED.
