# 074 — Historical BLIB WRITEO full-width octal

## Objective

Call the surviving historical `WRITEO(N)` (G!65) via the
persistent `HERC02.BCPL.OBJ(BLIB)` object member.
The source defines `WRITEO(N) BE WRITEOCT(N,11)`,
so the expected result is eleven octal digits, including leading zeroes.

`WRITEO(42)` must emit `00000000052`; delimiters make its
width visible. The test runs using the shared independent
application/runtime/BLIB object-link pathway, not a source combiner.

Expected exact output:

```text
>00000000052<
```

## Status

PENDING first TK5 execution.
