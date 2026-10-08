# 079 — Long formal list and address-of-argument vector

## Purpose

Regressions 075 and 076 prove the historical BLIB WRITEF loses the
third data argument (42/33 appears as 2) despite successful MVS
completion. Regression 078 proves that a *four-formal* local procedure
correctly handles the fourth argument in R10 and through `@A`.

The historical WRITEF is declared with twelve formals:
`WRITEF(FORMAT,A,B,C,D,E,F,G,H,I,J,K)`. This diagnostic duplicates
that precise signature while removing formatting entirely. The caller
supplies only `(0,11,22,33)`, as in ordinary variadic-style calls;
the callee uses only supplied arguments. It prints `(@A)!0`,
`(@A)!1`, `(@A)!2` and direct C using historical WRITEN.

Expected: `11 22 33 33`.

If 079 fails after 078 passed, focus instrumentation on CG370's
entry save mask, formal home offsets and workspace sizing for
many-formal procedures. If 079 passes, the problem instead depends
on BLIB WRITEF's body or the distinct compilation path used to
create the installed BLIB object.

Independent application/BCPLMAIN/persistent BLIB object pathway,
unchanged historical BLIB and BCPLMAIN.

## Status

PENDING TK5 execution.
