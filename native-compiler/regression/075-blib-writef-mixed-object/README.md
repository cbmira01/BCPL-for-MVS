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

PENDING TK5 execution.
