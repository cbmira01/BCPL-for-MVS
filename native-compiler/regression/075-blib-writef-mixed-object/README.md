# 075 — Historical BLIB WRITEF mixed arguments

## Objective

Test multiple format conversions in one call to the **historical BLIB**
`WRITEF` (G!76), using its own variadic argument cursor and dispatch.
The test passes a character, a packed BCPL string and a signed decimal
number, in that order, to the same formatter:

```bcpl
WRITEF("C:%C S:%S N:%N", 'Z', "HI", 42)
```

The expected output is `C:Z S:HI N:42`. This tests both multiple
argument advancement and three BLIB format operations (`%C`, `%S`,
`%N`) in a single native call. Unlike tests of the bootstrap BCPLMAIN
formatter, this calls the historical BLIB `WRITEF` via the shared
object-library module export.

## Build contract

The `object-blib.txt` marker selects independently assembled
application/BCPLMAIN control sections and link-edit of the resident
`HERC02.BCPL.OBJ(BLIB)` member. Neither BLIB nor the canonical
BCPLMAIN is recompiled or changed.

## Status

**FAIL — JOB 2583 (2026-10-09 guest date).** ASMAP, ASMRUN, LKED and GO all RC=0000, but actual output was `C:Z S:HI N:2`, not `C:Z S:HI N:42`. The generated application passes `'Z'` in R8, the packed `"HI"` string pointer in R9, and `42` in R10. The defect therefore occurs after argument setup, possibly in historical WRITEF's variadic argument storage/cursor or nested-call preservation. Do not accept `2` as expected behavior. Diagnostic regression 076 isolates the third argument.

## Validation after G!76 binding correction

**PASS** — user reran `tools/run-native-regression 75 76` after runtime commit `ab1d993`; the two tests passed, 0 failures. The originally observed third-argument truncation originated in BCPLMAIN's provisional `WRITEST` shadowing the imported historical BLIB G!76 binding. The corrected BCPLMAIN preserves BLIB's entry and uses bootstrap WRITEST only when G!76 remains unset. No CG370 or BLIB change was needed.
