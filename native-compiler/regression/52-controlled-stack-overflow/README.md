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

and terminates normally through the existing FINISH/MVS return path.

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
- terminate through the controlled WIP overflow path rather than S0C4/S322.

## Status

PENDING native run.
