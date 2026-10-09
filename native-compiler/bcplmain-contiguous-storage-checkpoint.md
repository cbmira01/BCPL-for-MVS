# BCPLMAIN contiguous startup storage — validation checkpoint

Status: **VALIDATED UNDER TK5 — 82 PASS / 0 FAIL (00–081)**.

The former static `GLOBV` (201 fullwords, including G!0) and `WORK` (4096 fullwords) have been replaced in `asm/bcplmain-wip.asm` with one 17,188-byte GETMAIN EC allocation. The first 804 bytes hold the global vector; the following 16,384 bytes hold the BCPL workspace. These sizes deliberately match the former static extents.

Startup records the block address and the start/end of workspace, initializes G!0 and global sentinels, publishes G!54/G!55, and sets STKLIM to the allocated end. The normal FINISH path and startup errors after allocation call FREEMAIN R. GETMAIN failure returns MVS code 24. This does **not** attempt to reconstruct historical PARM/HNUM/GNUM/INUM policy, STKLIM clearance semantics, or full cleanup of separately acquired GETVEC blocks.

## Acceptance plan (operator on TK5)

1. Pull `main`; inspect/assemble the modified `asm/bcplmain-wip.asm` using the established native regression runner.
2. Run a narrow smoke test of regressions 00 (entry/FINISH), 07 (global initialization), 27–30 (GETVEC/FREEVEC), 48–52 (stack checking), 069 (independent BLIB), 075/076 (BLIB WRITEF binding).
3. Inspect IFOX/IEWL/JES diagnostics and resolve any assembler addressability errors or MVS storage failures before asserting runtime success.
4. Once any shared-runtime change is stable, execute the **entire** `tools/run-native-regression` panel. Only record PASS after actual guest execution.

The prior observed baseline remains **82 PASS, 0 FAIL (00–081)**, *before* this storage change. It is not evidence of the modified runtime's correctness.

## Deliberate limitations

This remains a single-instance, non-reentrant WIP runtime with static control words and a private MVS save area. The requested block is fixed size; no historical stack clearance area has been introduced. Separately acquired vector blocks have their own lifecycle and are not implicitly released here. Normal termination still relies on existing output handling; explicit DCB CLOSE is separate work.

## Validation closeout — 2026-10-09

Operator ran the complete native regression suite on `main` after the GETMAIN register correction `f58b9d0`:

```text
NATIVE REGRESSION COMPLETE
PASS  82
FAIL  0
TOTAL 82
```

Earlier smoke checks: regression 000 PASS; 027–030 PASS (4/4); 048–052 PASS (5/5); 069 PASS; 075–076 PASS (2/2). The first smoke run abended S0C7 because startup temporarily overwrote R10, its active assembler base, with the GETMAIN length. Commit `f58b9d0` moved the length to R9. The second smoke and subsequent full panel passed. No BLIB or CG370 source changes were required.

**Validation scope:** This establishes compatibility with all 82 native regressions. The tests do not independently instrument MVS storage reclamation or establish the historical INITSAVE configuration/stack-clearance behavior. Those are future lifecycle tasks.
