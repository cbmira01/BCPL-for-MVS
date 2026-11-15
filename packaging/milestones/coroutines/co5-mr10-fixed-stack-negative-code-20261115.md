# CO.5 — MR10 fixed-stack probe unexpected interpreted CODE=-1

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Date:** 15 November 2026
**Tested GitHub main:** `803c5ba0c712a36c043f20da7cbc4987c17feb1d`
**Status:** FAIL, known qualified legacy startup-frame incompatibility (see 15 November diagnostic addendum)
**Evidence class:** OWNER-REPORTED INTERPRETED-MVS-TESTED; raw JES reports not independently reviewed

## Operator-reported focused regression campaign

- Coordinator evidence: `workarea/project-regressions/20261115T210217Z-27162-laq2a37x/`
- MR10 Development Probes: **7 PASS, 1 FAIL, 3 NOT_RUN**, 11 selected
- Failed accepted probe: `10-coroutines/fixed-stack-producer-consumer`
- Runner error: `interpreted CODE expected 0, got ['-1']`
- Coordinator and probe campaign: FAIL, RC=1; elapsed 13 seconds
- Full native Bootstrap, Runtime Extensions, BCPLTIME and BCPLQSAM campaigns remain NOT_RUN; earlier 13/13 native coroutine PASS at a different revision remains separately recorded

## Source-specific diagnosis and qualification

The golden contract requires `CODE=0` and ten alternating producer/consumer records. The unchanged BCPL probe uses a fixed local `VEC 100` stack and the reconstructed interpreted `CHANGECO`; it does not use native System/370 `BCPLCO`. Its last `PRODUCER` return value is `-1`, but the main source invokes `FINISH` after five yields and does not deliberately resume that producer after its fifth value.

The **same source/contract previously passed** with `CODE=0`, ten golden records and all-zero JES step codes on 11 November 2026 (JES job **5225**), as recorded in `co0-mr10-coroutine-jes-summary-review-20261111.md`. This does not prove the new MVS run was deterministic or healthy.

`mr10-kit-compiler/asm/icintv19.asm` returns `-1` on its generic `INTERROR` path, prints `INTCODE ERROR AT C = ...` and the recent-instruction ring, and returns via `INTRTN`. However, an explicit `X30` return using A=-1 is another possible source of a negative interpreted completion. **The numeric result alone does not identify the cause.** No source, expected-code or oracle change is justified without the actual failing JES report.

## Reproducible read-only evidence extraction

New source-controlled `tools/mr10/inspect-dev-probe-failure` reads only the existing project coordinator and child probe receipts under `workarea/`. It reports the exact failing case, job number, all interpreted phase codes, final printed records, error markers and the last 21 trace lines (if present), without submitting JES jobs or modifying datasets. Six assistant-executed host tests verify bounded output, fail-closed input provenance, actual FAIL classification and receipt parsing; Python syntax checked.

The next verification gate is to inspect the previously retained receipt from the failed campaign, compare its final `CODE=-1` with the actual `INTCODE ERROR`, `C` offset, `P`, recent decoded instructions, and last program records, and only then decide whether an isolated same-source reproduction or implementation repair is warranted.

No changes to accepted BCPL, IFOX, IEWL, ICINT, golden outputs, public globals or installed MVS objects. **CO.5 remains IN PROGRESS.**

## 15 November 2026 — focused JES 5499 diagnostic; historical qualification confirmed

**Original tested revision:** `803c5ba0c712a36c043f20da7cbc4987c17feb1d`.
**Read-only inspection tool revision:** `bdb89edb8de7d20c163b209f56164f39f3ca0a15`.
**Classification:** OWNER-REPORTED INTERPRETED-MVS-TESTED and
source-compared historical evidence. The raw local receipt was read by the
operator's source-controlled inspector, not directly inspected by the
assistant.

The operator ran `tools/mr10/inspect-dev-probe-failure
--project-evidence 20261115T210217Z-27162-laq2a37x` with extraction RC=0.

- Original coordinator: `workarea/project-regressions/20261115T210217Z-27162-laq2a37x/`
- Child receipt: `workarea/mr10-probes/20261115T210217Z-27166-z_esrvk5/`
- JES **5499**; compile-and-run runner RC=0; interpreted phase CODE **-1**
- `INTCODE ERROR AT C = 803`; no producer/consumer records
- Recent instruction trace: cycle 98 transfers via `X32`, cycle 99
  `LIG9` restores transfer value, cycle 100 `JIG10` branches to
  continuation 175839 (C-offset 801), cycle 101 decodes an invalid word.
- The independent JES step summaries were not attached to this review.

**Root-cause classification:** This exactly repeats accepted CO.0 JOB
**5318** (12 November 2026): 101 interpreter cycles, `INTCODE ERROR AT
C = 803`, `CODE=-1`, no program records. The authoritative
[CO.0 U01/U02 investigation and qualified disposition](co0-u01-static-interpreter-transfer-and-u02-five-probe-gate-20261112.md)
documents the reason: legacy static `MAKECO` writes `C!0 := C` and treats
descriptor fields as its first activation frame. The promoted canonical
MR10 `ICLIB` expects `C!0` to point to a saved CHANGECO call frame
with a valid `P!0`/ `P!1` and a `COBOOT` startup continuation.
`JIG10` therefore takes the legacy descriptor word as a code
continuation and fetches invalid INTCODE. This failure is **not**
evidence that the separately tested native System/370 coroutine switch
has regressed.

A separate source-preserved `fixed-stack-co0-candidate.bcpl` uses
`P=C+3`, `P!0=P`, `P!1=COBOOT` and the canonical compatible startup.
CO.0 JOB **5321** already verified its original ten-record golden,
interpreted `CODE=0`, and 10/10 zero-RC JES steps. That separate
success does **not** convert either JOB 5318 or JOB 5499 into a PASS.

**Next qualified CO.5 verification:** Run the three accepted probe
identities that were NOT_RUN after JOB 5499 (`resumeco-chain`,
`create-delete-static-pool`, `11-getvec-freevec`) separately, with
complete MVS receipts. Then run native/project suites independently;
do not claim the eleven-case `mr10-probes` coordinator suite passed,
and do not silently change, exclude, renumber, accept as SKIP, or rewrite
the known-incompatible accepted legacy test. A future explicit
release/suite contract decision must govern how the known qualified
incompatibility is represented in a unified regression acceptance gate.
CO.5 remains **IN PROGRESS**.
