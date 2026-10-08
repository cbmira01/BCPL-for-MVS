# 071 — Historical BLIB PACKSTRING in-place object regression

## Objective

Test the surviving `PACKSTRING(V,S)` (G!66) with **S=V**, exercising
its explicit overlapping-source/destination accommodation. The application
initializes an unpacked vector as `V!0=5`, `V!1..5='H','E','L','L','O'`,
then calls `PACKSTRING(V,V)`. The historical implementation preserves
`X=V!(N/4)` before clearing `S!(N/4)`, packs bytes by calling PUTBYTE,
restores the overlapping character with `PUTBYTE(S,N/4,X)`, and returns
`N/4`. For N=5 the expected result is 1.

If PACKSTRING returns 1, the application renders the packed result through
historical `WRITES` (G!60), yielding `HELLO`; otherwise it emits `!`.
This deliberately requires an in-place packed byte representation to work,
rather than simply echoing the original unpacked vector.

## Execution contract

The `object-blib.txt` marker routes this test through the independent
application / temporary BCPLMAIN / persistent `HERC02.BCPL.OBJ(BLIB)`
object pathway established by 069. BLIB is not recompiled and its source
is not combined with the application. `PACKSTRING` also exercises the
machine-code `PUTBYTE` (G!86) primitive installed by BCPLMAIN.

Expected exact BCPL output: `HELLO`.

## Status

**PASS** — user-executed `tools/run-native-regression 71` on TK5 (2026-10-08), exact output `HELLO`; 1 PASS, 0 FAIL. Historical PACKSTRING in-place and WRITES executed through persistent BLIB object.
