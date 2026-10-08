# 070 — Historical BLIB UNPACKSTRING via persistent object library

## Objective

Execute historical `UNPACKSTRING(S,V)` (G!67) directly from the
persistent `HERC02.BCPL.OBJ(BLIB)` object. The canonical BLIB is neither
demoted again nor compiled for this test.

The historical routine copies word `V!0` from the string's length byte
and fills each subsequent word `V!I` with the corresponding character
byte, for `I = 1..length`. The regression unpacks `"HELLO"` into a
local vector, verifies `V!0 = 5`, and renders the five vector elements
through BCPLMAIN's native WRCH, with no call to BLIB WRITES. This means
the displayed text must actually come from the unpacked vector.

Expected output: `HELLO`. Unexpected length emits `!`.

## Architectural path

`object-blib.txt` marks an independent object-library test.
The standard native runner compiles the application, uses the shared
regression 069 executable deck builder with entry `BCRG0070`, assembles
application and regression-local BCPLMAIN independently with IFOX,
includes installed BLIB from `HERC02.BCPL.OBJ(BLIB)` at IEWL, executes
GO, and checks the native output. This inherits 069's experimental
two-section registration; it is not the historical runtime module loader.

## Status

**PASS** — user-executed `tools/run-native-regression 70` on TK5 (2026-10-08), exact BCPL output `HELLO`; 1 PASS, 0 FAIL. This validates historical `UNPACKSTRING` from persistent BLIB with independent application/runtime/object linkage.
