# 52 - controlled stack overflow

This regression is the first native checked-stack boundary test.

It follows the historical checkpoint recorded in
`docs/stack-check-contract.md`. BCPLMAC proves that the original runtime kept
a byte-addressed safe stack limit distinct from the byte beyond allocated
stack, while BLIB maps system code `X'0D3'` to `STACK OVERFLOW`.

The original machine-code STKCK body is not present in the surviving source, so
this test exercises a documented WIP reconstruction rather than claiming the
exact historical comparison.

## Source shape

DEPTH is non-tail-recursive and owns `VEC 255` on every activation. That makes
each generated frame large enough to cross the current 16 KiB static WORK area
after only a modest number of recursive calls.

START asks for DEPTH(100), which must not return normally if the checked-stack
boundary is working.

## WIP runtime rule

The current reconstruction treats WORKEND as the provisional safe limit and
accepts a generated frame only when:

```text
W + inline-frame-size <= STKLIM
```

On failure, the bootstrap runtime emits:

```text
STACK OVERFLOW
```

and, in M2.1 D7, terminates through the common cleanup path with MVS GO RC=0012. Earlier D6 completed with RC=0000.

This output path is deliberately provisional. Historical BLIB reports stack
overflow as system code X'0D3' and ultimately STOP(100); full ABORT integration
is not yet reconstructed.

## Acceptance criteria

A successful Test 52 must:

- compile with CG370 stack checking enabled;
- generate a four-digit-or-larger checked frame for DEPTH;
- show recursive W advancement and ordinary BALR linkage;
- assemble and link normally;
- detect the stack boundary before uncontrolled storage corruption;
- emit exactly `STACK OVERFLOW`;
- require GO RC=0012 for the D7 candidate;
- terminate through the controlled WIP overflow path rather than S0C4/S322.

## Status

PASS — native run on 2026-10-07; emitted `STACK OVERFLOW`.

Observed DEPTH code:

```asm
BAL 14,60(11)
DC A(L994) STACK FRAME SIZE
...
LA 15,1044(5)
...
BALR 6,4
...
L994 EQU 1072 STACK FRAME SIZE
```

This is an important contract distinction: the recursive call advances W by
1044 bytes, but the checked entry requires 1072 bytes. The runtime therefore
must use the inline frame-size word for the boundary test rather than assuming
that the caller's W displacement equals the callee's full storage requirement.

The run crossed the 16 KiB WIP stack boundary through the controlled STKOVFL
path, emitted `STACK OVERFLOW`, and avoided uncontrolled storage corruption
or an MVS abend. Historical X'0D3'/ABORT/STOP(100) integration remains
unreconstructed.

## M2.1 D7 result (14 October 2026)

The first complete D7 panel (00–123) exercised this checked-recursion overflow in payload **JOB 3101 RG052R**: ASMAP RC=0000, LKED RC=0000, **GO RC=0012**, and the expected `STACK OVERFLOW` record matched. The harness reported FAIL because this case still lacked the nonzero-RC fixture, not because the runtime malfunctioned. `expected-go-rc.txt` now specifies `0012`, consistently with regression 093. Re-run on DEVOBJ(BCPLM7) to obtain an automated PASS.
