# G6 SAVEAREA minimal backing march — 2026-10-12

## Objective and bounded change

Extend the current BCPLMAIN R13 save-area backing so historical BLIB may read verified `SAVEAREA!29` and `SAVEAREA!48` without accessing beyond the declared save-area object. Preserve the first 18 words exactly as the MVS standard register-save area and preserve the existing G6 = R13 >> 2 publication.

## Historical evidence

`richards-bcpltape/km10/comacro`, USERSAVE macro: `USA` begins with 18 save-area words; `LOADLIST` is at byte offset 116 (index 29), `FREEBASE` at byte offset 192 (index 48). `richards-bcpltape/bcplib/bcpl/blib`: MAPSTORE and INPROGRAM read `SAVEAREA!29`, and VALIDPOINTER reads `SAVEAREA!48`; these are byte-address list heads. The historical macro is richer than this minimal compatibility backing. The `bcplmac` alternate variant uses VECLIST instead of FREEBASE and is not silently mixed in.

## Implementation staged in source

In both `asm/bcplmain-wip/30-control-data-and-end.asmfrag` and `asm/bcplmain-wip.asm`:

```asm
MSVSAVE  DS    18F
* Historical USERSAVE-compatible G6 list-head positions.
* The leading 18 words remain the ordinary MVS save area (R13).
* Unimplemented intervening fields are reserved, not emulated.
         DS    11F
MSVLOAD  DC    F'0'              G6!29, byte-pointer load-list head
         DS    18F
MSVFREE  DC    F'0'              G6!48, byte-pointer free-area head
```

Arithmetic: `MSVLOAD` = (18+11)*4 = 116; `MSVFREE` = (18+11+1+18)*4 = 192; complete region = 49*4 = 196 bytes. Both list heads are explicit zeros in the load module. The current native GETVEC's VECLIST is deliberately **not** reused as the historical FREEBASE list. Intervening fields are *not* claimed as implemented, and matching these two offsets does not constitute historical USERSAVE parity.

No edits to R13 entry linkage, G6 initialization, runtime object library, BLIB, BCPLMEM, or allocator implementation.

## Verification and acceptance (operator actions)

1. `git pull --ff-only`
2. `python3 tools/checks/check-bcplmain-modules.py`
3. `python3 tools/checks/check-asm-source.py asm/bcplmain-wip.asm`
4. `BCPL_RUNTIME_PDS=0 tools/run-native-regression 120 --show-output`
5. Optional focused consumer experiment after static and source-mode checks: native BCPL probe with `VALIDPOINTER` on a clearly invalid pointer and `INPROGRAM` outside program extents; neither should traverse a nonzero list or abend. Confirm exact test source before reporting semantic PASS.
6. `tools/run-native-regression` for full 121-case mixed-mode acceptance before installing a new PDS BCPLMAIN.

**Status:** source-only change committed; IFOX/TK5 and regressions not yet run, so not accepted for promotion. The installed production BCPLMAIN remains the last accepted baseline until verified and expressly promoted.

## Risks / future work

- Confirm assembler addressability and that all CSECT data references remain accessible following the enlarged static area.
- Standard save-area linkage is preserved structurally; validate in execution.
- Historical heap-region traversal and loader records still require separate producer/consumer investigation.
- The validity range `SAVEAREA<=N<STACKEND` is historically broad and must not be interpreted as a precise allocation-membership check without further evidence.
