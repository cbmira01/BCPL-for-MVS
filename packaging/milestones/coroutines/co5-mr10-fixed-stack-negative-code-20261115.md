# CO.5 — MR10 fixed-stack probe unexpected interpreted CODE=-1

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Date:** 15 November 2026
**Tested GitHub main:** `803c5ba0c712a36c043f20da7cbc4987c17feb1d`
**Status:** FAIL, source of unexpected code not yet demonstrated
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
