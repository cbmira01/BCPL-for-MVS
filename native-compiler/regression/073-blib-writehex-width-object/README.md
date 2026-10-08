# 073 — Historical BLIB WRITEHEX direct width

## Objective

Call the real historical `WRITEHEX(N,D)` (G!75), independently linked
from persistent `HERC02.BCPL.OBJ(BLIB)`. The historical implementation
emits exactly D hexadecimal digits using GETBYTE against an EBCDIC
digit lookup table, unlike the bootstrap numeric formatter.

Two calls exercise the width parameter directly: `WRITEHEX(42,4)`
must emit `002A`, and `WRITEHEX(42,8)` must emit `0000002A`.
Delimiters make digit counts unambiguous.

Expected output:

```text
>002A< >0000002A<
```

The test uses the marker-driven independent object-library pathway from
069–072 and does not recompile or alter BLIB or BCPLMAIN.

## Status

**PASS** — user-executed `tools/run-native-regression 73` on TK5 (2026-10-08), exact output `>002A< >0000002A<`; 1 PASS, 0 FAIL. Historical WRITEHEX executed through persistent BLIB object.
