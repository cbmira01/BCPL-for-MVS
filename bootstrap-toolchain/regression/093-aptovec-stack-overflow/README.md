# 093 — APTOVEC stack overflow protection

Status: **PENDING TK5**.

The test invokes G!40 APTOVEC with N=16380, at the provisional
APMAXN boundary. The vector plus callee linkage necessarily exceeds
the current 16,384-word safe stack extent once the caller's workspace
is included. APTOVEC must detect the overflow before invoking EXERCISE.

The callee deliberately prints `999` if reached. Correct execution
must not call it, and must not return to START. The existing controlled
stack-overflow exit writes `STACK OVERFLOW` to SYSPRINT and completes
normally with GO RC=0000, rather than producing a system ABEND.

Expected BCPL output: `STACK OVERFLOW` (and no `999`).

This is a limit test of the current 16,384-word stack implementation,
not a claim that 16,380 is a general historical APTOVEC limit.

## M4.4 BCPLM6/D6 profile reconciliation (2026-10-17)

The current description of GO RC0000 applies to the BCPLM6/D6
profile. A later D7/BCPLM7 cleanup contract expects GO RC0012,
recorded in the existing generic `expected-go-rc.txt`.
The separate `expected-go-rc-bcplm6.txt` now specifies RC0000
for the DEVOBJ(BCPLM6) compatibility panel. Both profiles retain
the mandatory `STACK OVERFLOW` output without calling EXERCISE.
